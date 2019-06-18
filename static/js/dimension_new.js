
function loadImg2(url, w, h) {
      var MIN_ZOOM = -1;
      var MAX_ZOOM = 5;
      var INITIAL_ZOOM = 1;
      var ACTUAL_SIZE_ZOOM = 3;
      var map2 = L.map('mapid', {
        minZoom: MIN_ZOOM,
        maxZoom: MAX_ZOOM,
        center: [0, 0],
        zoom: INITIAL_ZOOM,
        crs: L.CRS.Simple
      });


      var southWest = map2.unproject([0, h], ACTUAL_SIZE_ZOOM);
      var northEast = map2.unproject([w, 0], ACTUAL_SIZE_ZOOM);
      console.log(southWest, northEast);
      var bounds = new L.LatLngBounds(southWest, northEast);

      L.imageOverlay(url, bounds).addTo(map2);


      map2.setMaxBounds(bounds);
      map2.on('click', function(e) {
        var x= (e.latlng.lat)/(southWest.lat-northEast.lat);
        var y= (e.latlng.lng)/(-southWest.lng+northEast.lng);
        var grid = 'yes'//$("input[name=grid]:checked").val();

        console.log(x+':'+y+':'+grid+'hello');
        $('#loading2').html('<img src="loading.gif"> loading...');
        $('#table2').html('-');
        $('#table3').html('-');
        $.ajax({
          url: "/highlightPattern",
          data: {
            x: x,
            y:y,
            //datasetPath:getParameterByName('datasetPath'),
            id:''
            //grid:grid
          },
          contentType: 'application/json; charset=utf-8',
          success: function(result) {
            result=JSON.parse(result);
            //$("#div1").html("<img src='static/output/img_bea.png'></img>");
            console.log(result,result['rowPoints']);
            $('#table2').html(convertJsonToTable(JSON.parse(result['rowPoints'])));
            $('#table3').html(convertJsonToTable(JSON.parse(result['colPoints'])));
            drawParallelCoordinate('parallelPlot');
            //$('#jaccardMatrix').html(convertJsonToTable(JSON.parse(result['jaccard_matrix'])));
            $('#mapid2').remove();
            $('#parent2').append('<div id="mapid2" style="width: 500px; height: 400px;"></div>')
            d = new Date();
            loadImg2("/static/output/temp.png?" + d.getTime(), 2229, 2058);
            $('#loading2').html('-');
            var fname='output/legend.html?' + d.getTime()
            $('#legend2').load("{{ url_for('static',filename='fname') }}".replace('fname',fname))
            $('#loading2').html('-');
            console.log(JSON.parse(result['rowPoints']));
            console.log(JSON.parse(result['colPoints']));

            
          }
        });
    });
  }

function convertJsonToTable(data,type) {
    var tr;
    htmlstr2 = "<table border='1'>";
    var i = 0;
    htmlstr2 = htmlstr2.concat("<tr>")
    for (key in data[0]) {
      htmlstr2 = htmlstr2.concat("<th>" + key + "</th>")
    }
    htmlstr2 = htmlstr2.concat("</tr>")
    for (var i = 0; i < data.length; i++) {
      htmlstr2 = htmlstr2.concat('<tr>');
      for (key in data[i]) {
        if(key=='id')
        htmlstr2 = htmlstr2.concat("<td id='"+type+'_'+data[i][key]+"'>" + data[i][key] + "</td>");
        else
        htmlstr2 = htmlstr2.concat("<td>" + data[i][key] + "</td>");
      }
      htmlstr2 = htmlstr2.concat('</tr>');
    }
    htmlstr2 = htmlstr2.concat('</table>');
    return htmlstr2;
  }

function drawParallelCoordinate(container) {
  console.log('----drawParallelCoordinate-------');
  d = new Date();
  Plotly.d3.csv('/static/output/rowColPoints.csv?'+d.getTime(), function(err, rows) {
    colNames = d3.keys(rows[0]);
    console.log(colNames);
    function unpack(rows, key) {
      return rows.map(function(row) {
        return row[key];
      });
    }

    var dims=[];
    for (k in colNames) {
      k = colNames[k];
      if(k!='id' && k!='') {
      var t={};

      t['label']=k;
      t['values']=unpack(rows,k);
      dims.push(t);}
    }
    console.log('ddpdpd');
    console.log(dims);

    var data = [{
      type: 'parcoords',
      pad: [80, 80, 80, 80, 80],
      line: {
        color: unpack(rows, 'classLabel'),
        colorscale: [[0, 'red'], [0.5, 'green'], [1, 'blue']]
      },

      dimensions: dims
    }];

    var layout = {
      width: 800
    };

    Plotly.plot(container, data, layout);

  });
}
