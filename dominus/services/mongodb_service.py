import os
import logging
import socket
from typing import Dict, List, Optional, Tuple
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from ..core.config import MONGODB_URI, MONGODB_DATABASE, MONGODB_COLLECTION, MONGODB_SERVER_NAME, MONGODB_PRIORITY_STEP

SERVICE_NAME = os.getenv("SERVICE_NAME", "infra-status")


class MongoDBService:
    def __init__(self):
        self.mongodb_uri = MONGODB_URI
        self.database_name = MONGODB_DATABASE
        self.collection_name = MONGODB_COLLECTION
        # Use MongoDB server name if specified, otherwise fallback to hostname
        self.server_name = MONGODB_SERVER_NAME if MONGODB_SERVER_NAME else socket.gethostname()
        self.hostname = socket.gethostname()  # Keep for backward compatibility
        
    def _get_client(self) -> MongoClient:
        """Creates MongoDB connection"""
        try:
            client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Check connection
            client.admin.command('ping')
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logging.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _get_replica_set_status(self) -> Dict:
        """Gets replica set status"""
        client = self._get_client()
        try:
            # Get replica set status
            status = client.admin.command('replSetGetStatus')
            return status
        finally:
            client.close()
    
    def _get_current_member_info(self) -> Optional[Dict]:
        """Gets information about current replica set member"""
        try:
            status = self._get_replica_set_status()
            members = status.get('members', [])
            
            for member in members:
                member_name = member.get('name', '')
                # Check if member name contains our server name
                # Search both with port (mongodb1:27017) and without port (mongodb1)
                if self.server_name in member_name:
                    return member
                # Also check if member name starts with our server name
                if member_name.startswith(self.server_name + ':'):
                    return member
            return None
        except Exception as e:
            logging.error(f"Error getting current member info: {e}")
            return None
    
    def _get_all_members(self) -> List[Dict]:
        """Gets list of all replica set members"""
        try:
            status = self._get_replica_set_status()
            return status.get('members', [])
        except Exception as e:
            logging.error(f"Error getting members list: {e}")
            return []
    
    def _get_max_priority(self) -> int:
        """Gets maximum priority among all members"""
        members = self._get_all_members()
        max_priority = 0
        
        for member in members:
            priority = member.get('priority', 0)
            max_priority = max(max_priority, priority)
        
        return max_priority
    
    def _is_voter_server(self) -> bool:
        """Checks if current server is a voter (cannot change priority)"""
        try:
            current_member = self._get_current_member_info()
            if not current_member:
                return False
            
            # Get replica set configuration for exact priorities
            client = self._get_client()
            try:
                config = client.admin.command('replSetGetConfig')
                members = config['config']['members']
                
                # Find current server in configuration
                for member in members:
                    member_host = member.get('host', '')
                    if self.server_name in member_host or member_host.startswith(self.server_name + ':'):
                        priority = member.get('priority', 0)
                        votes = member.get('votes', 1)
                        
                        # If priority is 0 and votes > 0, then it's a voter
                        if priority == 0 and votes > 0:
                            logging.info(f"Server {self.server_name} is a voter (priority=0, votes={votes})")
                            return True
                        break
                        
            finally:
                client.close()
            
            # Also check if server is primary (primary cannot change its priority)
            state = current_member.get('state', 0)
            if state == 1:
                logging.info(f"Server {self.server_name} is primary and cannot change priority")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error checking server role: {e}")
            return False
    
    def get_current_status(self) -> str:
        """Determines current server status: primary, secondary or noset"""
        try:
            current_member = self._get_current_member_info()
            if not current_member:
                logging.warning(f"Current server {self.server_name} not found in replica set")
                return "noset"
            
            # Check server state in replica set
            state = current_member.get('state', 0)
            state_str = current_member.get('stateStr', 'UNKNOWN')
            
            # Determine status based on replica set state
            if state == 1 or state_str == 'PRIMARY':
                return "primary"
            elif state == 2 or state_str == 'SECONDARY':
                return "secondary"
            else:
                return "noset"
                
        except Exception as e:
            logging.error(f"Error determining status: {e}")
            return "noset"
    
    def promote_to_primary(self) -> bool:
        """Promotes current server priority to primary"""
        client = None
        try:
            # Check if current server is not a voter
            if self._is_voter_server():
                logging.error(f"Server {self.server_name} is a voter and cannot change priority")
                raise ValueError(f"Server {self.server_name} is a voter and cannot change priority")
            
            client = self._get_client()
            
            # Get current settings
            config = client.admin.command('replSetGetConfig')
            members = config['config']['members']
            
            # Find current server and its priority
            current_priority = 0
            current_member_found = False
            
            for member in members:
                member_host = member.get('host', '')
                # Check if host of our member contains our server name
                # Search both with port (mongodb1:27017) and without port (mongodb1)
                if self.server_name in member_host:
                    current_priority = member.get('priority', 0)
                    current_member_found = True
                    logging.info(f"Found current server {self.server_name} with priority {current_priority}")
                    break
                # Also check if member name starts with our server name
                if member_host.startswith(self.server_name + ':'):
                    current_priority = member.get('priority', 0)
                    current_member_found = True
                    logging.info(f"Found current server {self.server_name} with priority {current_priority}")
                    break
            
            if not current_member_found:
                logging.error(f"Current server {self.server_name} not found in configuration")
                return False
            
            # Find maximum priority among all servers
            max_priority = 0
            for member in members:
                priority = member.get('priority', 0)
                max_priority = max(max_priority, priority)
            
            logging.info(f"Maximum priority in cluster: {max_priority}")
            
            # Increase current server priority
            for member in members:
                member_host = member.get('host', '')
                # Check if host of our member contains our server name
                # Search both with port (mongodb1:27017) and without port (mongodb1)
                if self.server_name in member_host:
                    new_priority = max_priority + MONGODB_PRIORITY_STEP
                    member['priority'] = new_priority
                    logging.info(f"Increased server {self.server_name} priority from {current_priority} to {new_priority}")
                    break
                # Also check if member name starts with our server name
                if member_host.startswith(self.server_name + ':'):
                    new_priority = max_priority + MONGODB_PRIORITY_STEP
                    member['priority'] = new_priority
                    logging.info(f"Increased server {self.server_name} priority from {current_priority} to {new_priority}")
                    break
            
            # Apply new configuration
            config['config']['version'] += 1
            client.admin.command('replSetReconfig', config['config'])
            
            # Wait until server becomes primary
            import time
            max_wait_time = 30  # seconds
            wait_time = 0
            
            while wait_time < max_wait_time:
                time.sleep(2)
                wait_time += 2
                
                current_status = self.get_current_status()
                if current_status == "primary":
                    logging.info(f"Server {self.server_name} successfully became primary")
                    
                    # Wait a bit for configuration to fully apply
                    time.sleep(3)
                    
                    # Now normalize priorities of all servers by reducing them by a simple step
                    self._normalize_priorities()
                    return True
            
            logging.error(f"Server {self.server_name} did not become primary within {max_wait_time} seconds")
            return False
            
        except Exception as e:
            logging.error(f"Error promoting to primary: {e}")
            return False
        finally:
            if client:
                client.close()
    
    def _normalize_priorities(self) -> bool:
        """Normalizes all server priorities by reducing them by a simple step"""
        client = None
        try:
            client = self._get_client()
            
            # Get current settings
            config = client.admin.command('replSetGetConfig')
            members = config['config']['members']
            
            # Create list of servers with their priorities for sorting
            server_priorities = []
            for member in members:
                host = member.get('host', '')
                priority = member.get('priority', 0)
                server_priorities.append((host, priority, member))
            
            # Sort by priority (from lowest to highest)
            server_priorities.sort(key=lambda x: x[1])
            
            # Reduce priorities by simple step, starting from the lowest
            for host, priority, member in server_priorities:
                if priority > 0:  # Don't reduce priority 0
                    new_priority = max(0, priority - MONGODB_PRIORITY_STEP)
                    member['priority'] = new_priority
                    logging.info(f"Reduced server {host} priority from {priority} to {new_priority}")
            
            # Apply new configuration
            config['config']['version'] += 1
            client.admin.command('replSetReconfig', config['config'])
            
            logging.info("All server priorities normalized")
            return True
            
        except Exception as e:
            logging.error(f"Error normalizing priorities: {e}")
            return False
        finally:
            if client:
                client.close()


# Create global service instance
mongodb_service = MongoDBService()


def get_current_status() -> str:
    """Gets current server status"""
    return mongodb_service.get_current_status()


def promote_to_primary() -> bool:
    """Promotes current server to primary"""
    return mongodb_service.promote_to_primary()
