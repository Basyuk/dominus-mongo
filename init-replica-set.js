// Script for initializing MongoDB Replica Set
// Run on primary node after starting all MongoDB containers

rs.initiate({
  _id: "rs0",
  members: [
    {
      _id: 0,
      host: "msk-mng01:27017",
      priority: 500
    },
    {
      _id: 1,
      host: "vlg-mng01:27017", 
      priority: 400
    },
    {
      _id: 2,
      host: "msk-mnga01:27017",
      priority: 0,
      votes: 1
    }
  ]
});

// Wait until replica set becomes active
while (rs.status().ok !== 1) {
  sleep(1000);
}

print("Replica Set rs0 successfully initialized");
print("Primary: " + rs.status().members.find(m => m.state === 1).name);
