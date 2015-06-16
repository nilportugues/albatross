var Listing = function(albatross, pk){

  var self = this;

  this.albatross = albatross;
  this.pk = pk;

  this.data = null;
  self.languages = {};

  this.$languages = $("#language");
  this.$target = $("#tweets");

  this.populate_listing = function(){

    var url = albatross.urls.api.archives.subset.replace('0000', this.pk) +
      "?keys=user.screen_name,user.profile_image_url_https,text,favorite_count,retweet_count,geo.coordinates,lang,place.full_name,url";

    $.getJSON(url, function(data){
      self.data = data;
      if (Object.getOwnPropertyNames(self.languages).length == 0){
        for (var i = 0; i< data.length; i++){
          self.languages[data[i][8]] = data[i][8];
        }
        for (var language in self.languages){
          if (self.languages.hasOwnProperty(language)) {
            self.$languages.append('<option name="' + language + '">' + language + '</option>');
          }
        }
        self.$languages.change(self.render);
      }
      self.render();
    });

  };

  this.render = function(){

    var data = self.data;
    var language_restriction = self.$languages.val();

    self.$target.html("");
    for (var i = 0; i < data.length; i++) {

      var tweet = data[i];

      var user = {
        name: tweet[0],
        image: tweet[1],
        url: "https://twitter.com/" + tweet[0]
      };
      var text = tweet[2];
      var favourites = tweet[3].toString();
      var retweets = tweet[4].toString();
      var coordinates = tweet[5];
      var language = tweet[6];
      var location = tweet[7];
      var url = tweet[8];

      var map = "";
      if (coordinates) {
        map = ' <a href="https://www.google.nl/maps/@' + coordinates[1] + ',' + coordinates[1] + ',15z?hl=en" class="btn btn-xs btn-primary">' +
          '<i class="fa fa-map-marker fa-fw" title="' + location + '" data-toggle="tooltip"></i>' +
        '</a> ';
      }

      if (!language_restriction || language == language_restriction) {
        self.$target.append(
          '<div class="well tweet">' +
            '<div class="options">' +
              favourites + ' <i class="fa fa-star fa-fw text-warning" title="Favourites" data-toggle="tooltip"></i> ' +
              retweets + ' <i class="fa fa-retweet fa-fw text-success" title="Retweets" data-toggle="tooltip"></i> ' +
              map +
              '<a href="' + url + '" class="btn btn-xs btn-info" title="See this on Twitter" data-toggle="tooltip"><i class="fa fa-twitter fa-fw"></i></a>' +
            '</div>' +
            '<div class="image"><a href="' + user.url + '">' + Albatross().fallback_image(user.image) + '</a></div>' +
            '<div class="username"><a href="' + user.url + '">' + user.name + '</a></div>' +
            '<div class="text">' + text + '</div>' +
            '<div class="clearfix"></div>' +
          '</div>'
        );
      }

    }

    self.$target.find('[data-toggle="tooltip"]').tooltip();
    $(".tweet .text").tweetParser();

  };

  this.populate_listing();

  return this;

};
