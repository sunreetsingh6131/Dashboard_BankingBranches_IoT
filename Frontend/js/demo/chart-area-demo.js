// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = 'black';

var ctxL = document.getElementById("myAreaChart").getContext('2d');

var options = {
  scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                },
                scaleLabel: {
                     display: true,
                     labelString: 'No. of people',
                     fontSize: 20 
                  }
            }]            
        }  
};

var myLineChart = new Chart(ctxL, {
type: 'line',
data: {
labels: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
datasets: [{
  label: "ATM",
  data: [65, 59, 80, 81, 56, 55, 40],
  backgroundColor: [
  'rgba(0, 130, 312, .1)',
  ],
  borderColor: [
  '#4e73df',
  ],
      borderWidth: 2,
      pointBorderColor: "black",
      pointBackgroundColor: "white",
      pointBorderWidth: 1,
      pointHoverRadius: 8,
      pointHoverBackgroundColor: "#368ecc",
      pointHoverBorderColor: "white",
      pointHoverBorderWidth: 2,
      pointRadius: 4,
      pointHitRadius: 10,
  },
  {
  label: "Accounts",
  data: [28, 48, 40, 19, 86, 27, 90],
  backgroundColor: [
  'rgba(246, 200, 62, .2)',
  ],
  borderColor: [
  '#f6c23e',
  ],
      borderWidth: 2,
      borderWidth: 2,
      pointBorderColor: "black",
      pointBackgroundColor: "white",
      pointBorderWidth: 1,
      pointHoverRadius: 8,
      pointHoverBackgroundColor: "#368ecc",
      pointHoverBorderColor: "white",
      pointHoverBorderWidth: 2,
      pointRadius: 4,
      pointHitRadius: 10,
  },
  {
  label: "Exchange",
  data: [20, 40, 30, 10, 76, 17, 100],
  backgroundColor: [
  'rgba(28, 200, 138, .2)',
  ],
  borderColor: [
  '#1cc88a',
  ],
      borderWidth: 2,
      borderWidth: 2,
      pointBorderColor: "black",
      pointBackgroundColor: "white",
      pointBorderWidth: 1,
      pointHoverRadius: 8,
      pointHoverBackgroundColor: "#368ecc",
      pointHoverBorderColor: "white",
      pointHoverBorderWidth: 2,
      pointRadius: 4,
      pointHitRadius: 10,
  },
  {
  label: "General",
  data: [30, 50, 10, 20, 96, 30, 10],
  backgroundColor: [
  'rgba(231, 74, 59, .2)',
  ],
  borderColor: [
  '#e74a3b',
  ],
      borderWidth: 2,
      borderWidth: 2,
      pointBorderColor: "black",
      pointBackgroundColor: "white",
      pointBorderWidth: 1,
      pointHoverRadius: 8,
      pointHoverBackgroundColor: "#368ecc",
      pointHoverBorderColor: "white",
      pointHoverBorderWidth: 2,
      pointRadius: 4,
      pointHitRadius: 10,
  },
  {
  label: "Loans",
  data: [80, 40, 70, 60, 26, 97, 100],
  backgroundColor: [
  'rgba(102, 16, 242, .2)',
  ],
  borderColor: [
  '#6610f2',
  ],
      borderWidth: 2,
      borderWidth: 2,
      pointBorderColor: "black",
      pointBackgroundColor: "white",
      pointBorderWidth: 1,
      pointHoverRadius: 8,
      pointHoverBackgroundColor: "#368ecc",
      pointHoverBorderColor: "white",
      pointHoverBorderWidth: 2,
      pointRadius: 4,
      pointHitRadius: 10,
  }
  ]
  },
  options: options
});