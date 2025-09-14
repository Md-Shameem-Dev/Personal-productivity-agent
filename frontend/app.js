document.getElementById("taskForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const taskInput = document.getElementById("task");
  const task = taskInput.value;

  // Send task to backend
  const response = await fetch("http://127.0.0.1:8000/add_task", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task }),
  });

  const data = await response.json();
  const taskList = document.getElementById("taskList");
  const li = document.createElement("li");
  li.textContent = data.task;
  taskList.appendChild(li);

  taskInput.value = "";
});