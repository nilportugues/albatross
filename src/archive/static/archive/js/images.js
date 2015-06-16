var Images = function(albatross, pk){

  var self = this;

  this.albatross = albatross;
  this.pk = pk;

  this.$gallery = $("#gallery");
  this.$grid = this.$gallery.find(".grid");

  this.init = function(){

    // Rebuild the UI to go fullscreen
    $("#global-container").removeClass("container").addClass("col-xs-12");

    var url = self.albatross.urls.api.archives.distillation.images.replace(
      '0000', this.pk);

    $.getJSON(url, function(data) {

      for (var i = 0; i < data.length; i++){
        var url = data[i][0];
        var weight = data[i][1];
        var tweet_url = data[i][2];
        var users = data[i][3].join(",");
        var additional_classes = (weight > 1) ? 'grid-item-weight' + weight.toString() : '';
        self.$grid.append(
          '<div ' +
            'data-toggle="modal" ' +
            'data-target="#lightbox" ' +
            'data-tweet="' + tweet_url + '" ' +
            'data-users="' + users + '" ' +
            'class="grid-item ' + additional_classes + '"' +
          '>' +
            '<img src="' + url + '" />' +
          '</div>'
        );
      }

      self.$grid.imagesLoaded(function(){

        self.$grid.masonry({
          itemSelector: '.grid-item',
          percentPosition: true,
          columnWidth: '.grid-sizer'
        });
        $(".loading").remove();

        self.$gallery.prepend('<p class="lead">' +
          'The images below are scaled by the frequency of their appearance ' +
          'during the capture window.' +
        '</p>');

        self.$grid.addClass("show");

        // Actually a bootstrap modal, but whatever.
        $('#lightbox').on('show.bs.modal', function(event){

          var $relatedTarget = $(event.relatedTarget);

          var url = $relatedTarget.find("img").attr("src");

          var source = $relatedTarget.data("tweet");

          var users = $relatedTarget.data("users");
          users = (users) ? users.split(",") : [];

          var $html = $('<div></div>');

          $html.append('<a href="' + source + '"><img src="' + url + '" /></a>');
          $html.append('<div class="clearfix col-xs-12 source"><a href="' + source + '" class="btn btn-block btn-xs btn-primary"><i class="fa fa-twitter"></i> Source</a></div>');

          var $users = $('<div class="clearfix users"></div>');
          for (var j = 0; j < users.length; j++) {
            $users.append(
              '<a class="user" href="https://twitter.com/' + users[j] + '">' + users[j] + '</a> '
            );
          }
          $html.append($users);
          $html.append('<div class="clearfix"></div>');

          $(this).find('.modal-body').html($html);
        });

      });

    });

  };

  $(document).ready(function(){
    self.init();
  });

  return this;

};
