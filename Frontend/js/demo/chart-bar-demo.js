Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = 'black';

fetch('http://34.87.233.248:5000/show/timelogs')
  .then((response) => {
    return response.json();
  })
  .then((data) => {
    console.log(data['time'])
    var ctx = document.getElementById("barChart").getContext('2d');
    var data = {
      labels: ["9:00", "10:00", "11:00", "12:00", "1:00", "2:00", "3:00", "4:00", "5:00"],
      datasets: [{
          label: "People per hour",
          // fill: true,
          lineTension: 0.1,
          backgroundColor: "rgba(54, 185, 204,0.2)",
          borderColor: "#36b9cc",
          borderCapStyle: 'butt',
          borderDash: [],
          borderDashOffset: 0.0,
          borderJoinStyle: 'miter',
          pointBorderColor: "white",
          pointBackgroundColor: "black",
          pointBorderWidth: 1,
          pointHoverRadius: 8,
          pointHoverBackgroundColor: "brown",
          pointHoverBorderColor: "yellow",
          pointHoverBorderWidth: 2,
          pointRadius: 4,
          pointHitRadius: 10,
          // notice the gap in the data and the spanGaps: false
          data: data['time'],
          spanGaps: false,
        }
      ]
    };

    // Notice the scaleLabel at the same level as Ticks
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

    // Chart declaration:
    var myBarChart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: options
    });
  });


