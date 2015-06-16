var Map = function(albatross, pk){

  var self = this;

  this.albatross = albatross;
  this.pk = pk;
  this.$map_container = $("#map-container");
  this.map = null;

  // Rebuild the UI to go fullscreen
  $("#global-container").removeClass("container").addClass("col-xs-12");

  this.draw_map = function(){

    this.map = L.map('map').setView([0, 0], 9);

    L.tileLayer('http://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.png', {
      attribution: [
        'Map tiles by <a href="http://stamen.com">Stamen Design</a>, ',
        '<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> ',
        '&mdash; Map data &copy; ',
        '<a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      ].join(""),
      subdomains: 'abcd',
      minZoom: 1,
      maxZoom: 16,
      ext: 'png'
    }).addTo(this.map);

  };

  this.populate_map = function(data){

    self.draw_map();

    var features = [];
    for (var i = 0; i < data.length; i++) {
      var tweet = data[i];
      features.push({
        type: "Feature",
        properties: {
          id: tweet[0],
          user: tweet[1],
          text: tweet[2],
          image: tweet[3]
        },
        geometry: {
          type: "Point",
          coordinates: tweet[4]
        }
      });
    }

    if (!features.length){
      self.$map_container.html('<div class="sadface">Unfortuantely, none of the tweets recorded contained geographical data.</div>');
      return;
    }

    var cluster = L.markerClusterGroup({
      showCoverageOnHover: false,
      spiderfyOnMaxZoom: true
    });
    var markers = L.geoJson(features, {
      onEachFeature: function(feature, layer){
        layer.bindPopup(feature.properties.text);
        layer.on("popupopen", function(e){
          var $tweet = $('<div>' +
            '<div class="user pull-left"><a href="https://twitter.com/' + feature.properties.user + '"><img src="' + feature.properties.image + '" style="width: 50px;" /></a></div>' +
            '<div class="tweet">' + feature.properties.text + '</div>' +
            '<div class="more text-right"><a href="https://twitter.com/' + feature.properties.user + '/status/' + feature.properties.id + '">More info</a></div>' +
          '</div>');
          e.popup.setContent($tweet.html());
          $(".leaflet-popup-content .tweet").tweetParser();
        });
      },
      pointToLayer: function (feature, latlng) {
        return L.circleMarker(latlng, {
          radius: 10,
          fillColor: "#008CBA",
          color: "#000",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.5
        });
      }
    });

    cluster.addLayer(markers);
    self.map.addLayer(cluster);

    self.map.fitBounds(markers.getBounds());

    $(".loading").remove();

  };

  $.getJSON(
    self.albatross.urls.api.archives.distillation.map.replace('0000', this.pk),
    self.populate_map
  );

  return this;

};
