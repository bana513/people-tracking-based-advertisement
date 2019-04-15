// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
  // *     example: number_format(1234.56, 2, ',', ' ');
  // *     return: '1 234,56'
  number = (number + '').replace(',', '').replace(' ', '');
  var n = !isFinite(+number) ? 0 : +number,
    prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
    sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
    dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
    s = '',
    toFixedFix = function(n, prec) {
      var k = Math.pow(10, prec);
      return '' + Math.round(n * k) / k;
    };
  // Fix for IE parseFloat(0.55).toFixed(0) = 0;
  s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
  if (s[0].length > 3) {
    s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
  }
  if ((s[1] || '').length < prec) {
    s[1] = s[1] || '';
    s[1] += new Array(prec - s[1].length + 1).join('0');
  }
  return s.join(dec);
}

Number.prototype.pad = function(size) {
    var s = String(this);
    while (s.length < (size || 2)) {s = "0" + s;}
    return s;
}

var ctx = document.getElementById("myAreaChart");
var myLineChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: "People on camera",
      lineTension: 0.25,
      backgroundColor: "rgba(78, 115, 223, 0.05)",
      borderColor: "rgba(78, 115, 223, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(78, 115, 223, 1)",
      pointBorderColor: "rgba(78, 115, 223, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
      pointHoverBorderColor: "rgba(78, 115, 223, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: [],
    },{
      label: "OUT",
      lineTension: 0.25,
      backgroundColor: "rgba(231,74,59, 0.05)",
      borderColor: "rgba(231,74,59, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(231,74,59, 1)",
      pointBorderColor: "rgba(231,74,59, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(231,74,59, 1)",
      pointHoverBorderColor: "rgba(231,74,59, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: [],
    },{
      label: "IN",
      lineTension: 0.25,
      backgroundColor: "rgba(28,200,138, 0.05)",
      borderColor: "rgba(28,200,138, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(28,200,138, 1)",
      pointBorderColor: "rgba(28,200,138, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(28,200,138, 1)",
      pointHoverBorderColor: "rgba(28,200,138, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: [],
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
          unit: 'time'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          maxTicksLimit: 5,
          padding: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return number_format(value);
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
      display: true
    },
    tooltips: {
        enabled: false,
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        titleMarginBottom: 10,
        titleFontColor: '#6e707e',
        titleFontSize: 14,
        borderColor: '#dddfeb',
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        intersect: false,
        mode: 'index',
        caretPadding: 10,
        callbacks: {
            label: function (tooltipItem, chart) {
                var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                return datasetLabel + ': $' + number_format(tooltipItem.yLabel);
            }
        }
    }
  }
});

var ctx2 = document.getElementById("myAreaChart2");
var myLineChart2 = new Chart(ctx2, {
  type: 'line',
  data: {
    labels: [],
    datasets: [{
      label: "LEFT",
      lineTension: 0.25,
      backgroundColor: "rgba(231,74,59, 0.05)",
      borderColor: "rgba(231,74,59, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(231,74,59, 1)",
      pointBorderColor: "rgba(231,74,59, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(231,74,59, 1)",
      pointHoverBorderColor: "rgba(231,74,59, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: [],
    },{
      label: "RIGHT",
      lineTension: 0.25,
      backgroundColor: "rgba(28,200,138, 0.05)",
      borderColor: "rgba(28,200,138, 1)",
      pointRadius: 3,
      pointBackgroundColor: "rgba(28,200,138, 1)",
      pointBorderColor: "rgba(28,200,138, 1)",
      pointHoverRadius: 3,
      pointHoverBackgroundColor: "rgba(28,200,138, 1)",
      pointHoverBorderColor: "rgba(28,200,138, 1)",
      pointHitRadius: 10,
      pointBorderWidth: 2,
      data: [],
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
          unit: 'time'
        },
        gridLines: {
          display: false,
          drawBorder: false
        },
        ticks: {
          maxTicksLimit: 7
        }
      }],
      yAxes: [{
        ticks: {
          maxTicksLimit: 5,
          padding: 10,
          // Include a dollar sign in the ticks
          callback: function(value, index, values) {
            return number_format(value);
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
      display: true
    },
    tooltips: {
        enabled: false,
        backgroundColor: "rgb(255,255,255)",
        bodyFontColor: "#858796",
        titleMarginBottom: 10,
        titleFontColor: '#6e707e',
        titleFontSize: 14,
        borderColor: '#dddfeb',
        borderWidth: 1,
        xPadding: 15,
        yPadding: 15,
        displayColors: false,
        intersect: false,
        mode: 'index',
        caretPadding: 10,
        callbacks: {
            label: function (tooltipItem, chart) {
                var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                return datasetLabel + ': $' + number_format(tooltipItem.yLabel);
            }
        }
    }
  }
});

if (!!window.EventSource) {
  var source = new EventSource('/number_of_people');
  source.onmessage = function(e) {
      // // console.log(myLineChart);
      // var chart = myLineChart.config.data;
      // // console.log();
      // var d = parseInt(e.data, 0);
      // chart.datasets[0].data.push(d);
      // chart.labels.push(e.data);
      // if(chart.datasets[0].data.length > 30){
      //    chart.datasets[0].data.splice(0, 1);
      //    chart.labels.splice(0, 1);
      // }
      // myLineChart.update();
      // console.log(myLineChart);

      console.log(e.data);
      var chart = myLineChart.config.data;
      var chart2 = myLineChart2.config.data;

      var data_array = e.data.split(";");
      var data_array_int = data_array.map(function(e) {
          e = parseInt(e, 0);
          return e;
        });

      var time = Math.floor(data_array_int[0]/60).toString() + ":" + (data_array_int[0]%60).pad(2);

      chart.datasets[0].data.push(data_array_int[1]);
      chart.datasets[1].data.push(data_array_int[2]);
      chart.datasets[2].data.push(data_array_int[3]);
      chart.labels.push(time);

      chart2.datasets[0].data.push(data_array_int[4]);
      chart2.datasets[1].data.push(data_array_int[5]);
      chart2.labels.push(time);


      if(chart.labels.length > 30){
         chart.datasets[0].data.splice(0, 1);
         chart.datasets[1].data.splice(0, 1);
         chart.datasets[2].data.splice(0, 1);
         chart.labels.splice(0, 1);

         chart2.datasets[0].data.splice(0, 1);
         chart2.datasets[1].data.splice(0, 1);
         chart2.labels.splice(0, 1);
      }
      myLineChart.update();
      myLineChart2.update();
  }
}

if (!!window.EventSource) {
  var source = new EventSource('/number_of_people');
  source.onmessage = function(e) {
      // // console.log(myLineChart);
      // var chart = myLineChart.config.data;
      // // console.log();
      // var d = parseInt(e.data, 0);
      // chart.datasets[0].data.push(d);
      // chart.labels.push(e.data);
      // if(chart.datasets[0].data.length > 30){
      //    chart.datasets[0].data.splice(0, 1);
      //    chart.labels.splice(0, 1);
      // }
      // myLineChart.update();
      // console.log(myLineChart);

      console.log(e.data);
      var chart = myLineChart.config.data;
      var chart2 = myLineChart2.config.data;

      var data_array = e.data.split(";");
      var data_array_int = data_array.map(function(e) {
          e = parseInt(e, 0);
          return e;
        });

      var time = Math.floor(data_array_int[0]/60).toString() + ":" + (data_array_int[0]%60).pad(2);

      chart.datasets[0].data.push(data_array_int[1]);
      chart.datasets[1].data.push(data_array_int[2]);
      chart.datasets[2].data.push(data_array_int[3]);
      chart.labels.push(time);

      chart2.datasets[0].data.push(data_array_int[4]);
      chart2.datasets[1].data.push(data_array_int[5]);
      chart2.labels.push(time);


      if(chart.labels.length > 30){
         chart.datasets[0].data.splice(0, 1);
         chart.datasets[1].data.splice(0, 1);
         chart.datasets[2].data.splice(0, 1);
         chart.labels.splice(0, 1);

         chart2.datasets[0].data.splice(0, 1);
         chart2.datasets[1].data.splice(0, 1);
         chart2.labels.splice(0, 1);
      }
      myLineChart.update();
      myLineChart2.update();
  }

  var description = document.getElementById("advertisementMessage");
  var description_source = new EventSource('/advertisement_description');
  description_source.onmessage = function(e) {
      console.log(e.data);
      description.innerHTML = e.data;
  }
}
