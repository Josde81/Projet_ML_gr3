//import {get_file, number_format} from 'utilities.js';
// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function set_langage_de_prog_data(result)
{
 var result_obj = JSON.parse(result);
 var labels = []
 var values = []
 param = window.location.pathname.split("/").pop()

var langage_de_prog_titre = document.getElementById("langage_de_prog_titre");
 if (param == "toutes")
 {
    langage_de_prog_titre.innerHTML = "Salaire - Toute la France";
 }
 else
 {
    langage_de_prog_titre.innerHTML = "Salaire - " + param;
 }


 for (item in result_obj)
 {
    var key =  "_" + param
    if  (item.indexOf(key) != -1)
    {
        labels.push(item.replace(key,""))
        values.push(result_obj[item])
    }
 }
 // Bar Chart Example
var ctx = document.getElementById("myBarChart");
var myBarChart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: labels,
    datasets: [{
      label: "Salaire",
      backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc','#fd7e14','#6610f2','#1cc88a','#e74a3b','#5a5c69','#0f6848','#4e73df', '#1cc88a', '#36b9cc','#fd7e14','#6610f2','#1cc88a','#e74a3b','#5a5c69','#0f6848'],
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf','#fdcea7','#9967ea','#7ec5ac','#e0928a','#88898e','#1eb57f','#2e59d9', '#17a673', '#2c9faf','#fdcea7','#9967ea','#7ec5ac','#e0928a','#88898e','#1eb57f'],
      borderColor: "#4e73df",
      data: values,
    }],
  },
  options: {
    maintainAspectRatio: false,
    layout: {
      padding: {
        left: 10,
        right: 25,
        top: 25,
        bottom: 0
      }
    },
    scales: {
      xAxes: [{
        time: {
          unit: 'month'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 20
        },
        maxBarThickness: 25,
      }],
      yAxes: [{
        ticks: {
          min: 0,
          max: (Math.max.apply(Math,values) + 1000),
          maxTicksLimit: 5,
          padding: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return  number_format(value) + '€ ';
          }
        },
        gridLines: {
          color: "rgb(234, 236, 244)",
          zeroLineColor: "rgb(234, 236, 244)",
          drawBorder: false,
          borderDash: [2],
          zeroLineBorderDash: [2]
        }
      }],
    },
    legend: {
      display: false
    },
    tooltips: {
      titleMarginBottom: 10,
      titleFontColor: '#6e707e',
      titleFontSize: 14,
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
      callbacks: {
        label: function(tooltipItem, chart) {
          var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
          return datasetLabel + ': $' + number_format(tooltipItem.yLabel);
        }
      }
    },
  }
});
}
get_file('http://127.0.0.1:5000/salaire_langage_de_prog/data', set_langage_de_prog_data)


function set_lang_de_prog_popularity(result)
{
  var result_obj = JSON.parse(result);
 var labels = []
 var values = []
 param = window.location.pathname.split("/").pop()

var langage_de_prog_titre = document.getElementById("langage_de_prog_popularity_titre");
 if (param == "toutes")
 {
    langage_de_prog_titre.innerHTML = "Popularité - Toute la France";
 }
 else
 {
    langage_de_prog_titre.innerHTML = "Popularité - " + param;
 }


 for (item in result_obj)
 {
    var key =  "_" + param
    if  (item.indexOf(key) != -1)
    {
        labels.push(item.replace(key,""))
        values.push(result_obj[item])
    }
 }

 var ctx = document.getElementById("myPieChart");
var myPieChart = new Chart(ctx, {
  type: 'pie',
  data: {
    labels: labels,
    datasets: [{
      data: values,
      backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc','#fd7e14','#6610f2','#1cc88a','#e74a3b','#5a5c69','#0f6848','#4e73df', '#1cc88a', '#36b9cc','#fd7e14','#6610f2','#1cc88a','#e74a3b','#5a5c69','#0f6848'],
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf','#fdcea7','#9967ea','#7ec5ac','#e0928a','#88898e','#1eb57f','#2e59d9', '#17a673', '#2c9faf','#fdcea7','#9967ea','#7ec5ac','#e0928a','#88898e','#1eb57f'],
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
      xPadding: 5,
      yPadding: 5,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 50,
  },
});


}
get_file('http://127.0.0.1:5000/salaire_langage_de_prog/popularity', set_lang_de_prog_popularity)
