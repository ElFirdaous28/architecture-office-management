import Chart from "chart.js/auto";

const projectDataElement = document.getElementById("project-chart-data");
const taskDataElement = document.getElementById("task-chart-data");

if (projectDataElement && taskDataElement) {
    const projectData = JSON.parse(projectDataElement.textContent);
    const taskData = JSON.parse(taskDataElement.textContent);

    const projectCanvas = document.getElementById("projectChart");
    const taskCanvas = document.getElementById("taskChart");

    if (projectCanvas) {
        new Chart(projectCanvas, {
            type: "doughnut",
            data: {
                labels: projectData.labels,
                datasets: [{
                    data: projectData.data,
                    backgroundColor: ["#94A3B8", "#C86446", "#2B7A78"],
                    borderWidth: 0,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                    },
                },
            },
        });
    }

    if (taskCanvas) {
        new Chart(taskCanvas, {
            type: "bar",
            data: {
                labels: taskData.labels,
                datasets: [{
                    label: "Tasks",
                    data: taskData.data,
                    backgroundColor: "#2B4C7E",
                    borderRadius: 6,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0,
                        },
                    },
                },
                plugins: {
                    legend: {
                        display: false,
                    },
                },
            },
        });
    }
}