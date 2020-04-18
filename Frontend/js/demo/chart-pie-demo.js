// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// Pie Chart Example

//http://0.0.0.0:5000/show/alltickets


fetch('http://34.87.233.248:5000/show/feedback')
  .then((response) => {
    return response.json();
  })
  .then((data) => {
    var feebacksarray = [];
    feebacksarray.push(data.Poor);
    feebacksarray.push(data.Okay);
    feebacksarray.push(data.Good);
    feebacksarray.push(data.Excellent);
    feebacksarray.push(data.Outstanding);

    var ctx = document.getElementById("myPieChart");
    var myPieChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ["Poor", "Okay", "Good", "Excellent", "Outstanding"],
        datasets: [{
          data: feebacksarray,
          backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc', '#c81c5a', '#c88a1c'],
          hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf', '#b41951', '#b47c19'],
          hoverBackground: "&#128533;",
          hoverBorderColor: "rgba(234, 236, 244, 1)",
        }],
      },
      options: {
        maintainAspectRatio: false,
        tooltips: {
          backgroundColor: "rgb(255,255,255)",
          bodyFontColor: "#858796",
          borderColor: '#dddfeb',
          borderWidth: 1,
          xPadding: 15,
          yPadding: 15,
          displayColors: false,
          caretPadding: 10,
        },
        legend: {
          display: false
        },
        cutoutPercentage: 80,
      },
    });
  });


