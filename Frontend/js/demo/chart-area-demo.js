// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = 'black';

// FETCH PREDICTIONS FOR PREDICTION CHART
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


chq_list = [];
gen_list = [];
acc_list = [];
lon_list = [];
exc_list = [];
atm_list = [];

fetch('http://34.87.233.248:5000/show/predictions')
  .then((response) => {
    return response.json();
  })
  .then((data) => {
    console.log("here")
    chq_list = data['Cheques'];
    gen_list = data['General'];
    acc_list = data['Accounts'];
    lon_list = data['Loans'];
    exc_list = data['Exchange'];
    atm_list = data['ATM'];
    var myLineChart = new Chart(ctxL, {
    type: 'line',
    data: {
    labels: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    datasets: [{
      label: "Exchange",
      data: exc_list,
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
      label: "ATM",
      data: atm_list,
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
      label: "Accounts",
      data: acc_list,
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
      data: gen_list,
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
      data: lon_list,
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

  });
    



