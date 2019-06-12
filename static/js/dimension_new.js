function loadImg(url, w, h) {
  var MIN_ZOOM = -1;
  var MAX_ZOOM = 5;
  var INITIAL_ZOOM = 1;
  var ACTUAL_SIZE_ZOOM = 3;
  var map = L.map('mapid', {
    minZoom: MIN_ZOOM,
    maxZoom: MAX_ZOOM,
    center: [0, 0],
    zoom: INITIAL_ZOOM,
    crs: L.CRS.Simple
  });


  var southWest = map.unproject([0, h], ACTUAL_SIZE_ZOOM);
  var northEast = map.unproject([w, 0], ACTUAL_SIZE_ZOOM);
  console.log(southWest, northEast);
  var bounds = new L.LatLngBounds(southWest, northEast);

  L.imageOverlay(url, bounds).addTo(map);



  map.setMaxBounds(bounds);
  map.on('click', function(e) {
    var x = (e.latlng.lat) / (southWest.lat - northEast.lat);
    var y = (e.latlng.lng) / (-southWest.lng + northEast.lng);
    console.log(x + ':' + y);
    var gridPatterns = $("input[name=ptype]:checked").val();
    var grid = $("input[name=grid]:checked").val();
    console.log(gridPatterns+' '+grid);
    $('#loading').html('<img src="loading.gif"> loading...');
    $('#table2').html('-');
    $('#table3').html('-');

    $.ajax({
      url: "/highlightPattern",
      data: {
        x: x,
        y: y,
        datasetPath: getParameterByName('datasetPath'),
        id: '',
        gridPatterns:gridPatterns,
        grid: grid
      },
      contentType: 'application/json; charset=utf-8',
      success: function(result) {
        //$("#div1").html("<img src='static/output/img_bea.png'></img>");
        result = JSON.parse(result);
        subspace = result['dim'].split(" ");
        console.log('subspace'+subspace);
        console.log(JSON.parse(result['rowPoints']));
        console.log(JSON.parse(result['colPoints']));
        console.log(JSON.parse(result['dist']), JSON.parse(result['pair']));
        $('#mapid').remove();
        $('#parent').append('<div id="mapid" style="width: 500px; height: 400px;"></div>')
        d = new Date();
        loadImg("/static/output/temp.png?" + d.getTime(), 2229, 2058);
        $('#loading').html('-');
        var fname = 'output/legend.html?' + d.getTime();
        $('#legend').load("{{ url_for('static',filename='fname') }}".replace('fname', fname));
        $('#loading').html('-');
        $('#table2').html(convertJsonToTable(JSON.parse(result['rowPoints']),'col'));
        $('#table3').html(convertJsonToTable(JSON.parse(result['colPoints']),'row'));
        //drawGraph(JSON.parse(result['dist']), JSON.parse(result['pair']));
        drawParallelCoordinate('parallelPlot');
        drawGiantWheel('#windrose1');
        drawPointsComparison(subspace, 'pointsPlot1', 'pointsPlot2');

      }
    });
  });
}


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
            datasetPath:getParameterByName('datasetPath'),
            id:'',
            grid:grid
          },
          contentType: 'application/json; charset=utf-8',
          success: function(result) {
            result=JSON.parse(result);
            //$("#div1").html("<img src='static/output/img_bea.png'></img>");
            console.log(result,result['rowPoints']);
            $('#mapid2').remove();
            $('#parent2').append('<div id="mapid2" style="width: 500px; height: 400px;"></div>')
            d = new Date();
            loadImg2("/static/output/temp.png?" + d.getTime(), 2229, 2058);
            $('#loading2').html('-');
            var fname='output/legend.html?' + d.getTime()
            $('#legend2').load("{{ url_for('static',filename='fname') }}".replace('fname',fname))
            $('#loading2').html('-');
            $('#table2').html(convertJsonToTable(JSON.parse(result['rowPoints'])));
            $('#table3').html(convertJsonToTable(JSON.parse(result['colPoints'])));

          }
        });
    });
  }