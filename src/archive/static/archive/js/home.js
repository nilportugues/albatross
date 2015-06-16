var Home = function(albatross, user_id){

  var self = this;

  this.albatross = albatross;
  this.$duration_select = $(".duration-selector select");
  this.$archives = $("#archives");
  this.user_id = user_id;
  this.$filters = $(".isotope-filters");

  /**
   *
   * Make the collection creation form prettier with nice buttons for the
   * select box.
   *
   */
  this.buttonify_select = function($select){

    $select.hide();

    var $button_block = $('<div class="btn-group" role="group"></div>');
    $select.find("option").each(function(){
      var $this = $(this);
      var selected = ($this.is(':selected')) ? " btn-primary" : "";
      $button_block.append(
        '<button type="button" class="btn btn-default' + selected + '" data-value="' + $this.val() + '">' + $this.text() + '</button>');
    });
    $select.after($button_block);

    var $buttons = $button_block.find("button");
    $button_block.find("button").click(function(){
      var $this = $(this);
      $buttons.removeClass("btn-primary");
      $this.addClass("btn-primary").blur();
      $select.val($this.attr("data-value"));
    });

  };

  this.populate_archives = function(url){

    $.getJSON(url, function(data){

      var results = data.results;

      for (var i = 0; i < results.length; i++) {

        var row = results[i];

        var compiling = '<i class="fa fa-cogs fa-fw help" data-toggle="tooltip" title="Compiling"></i> Compiling';
        var not_available = '<i class="fa fa-times" data-toggle="tooltip" title="No data available"></i> No Data Available';
        var blank = "";

        var total = (row.total) ? row.total : compiling;
        var size = (row.size) ? filesize(row.size) : compiling;

        var download = compiling;
        var as_text = compiling;
        var as_cloud = compiling;
        var as_statistics = compiling;
        var as_images = compiling;
        var as_map = compiling;

        var query = row.query;

        if (row.total) {

          download = '<a class="btn btn-success btn-block hidden-xs" href="' + row.raw + '" data-toggle="tooltip" title="Download the raw data"><i class="fa fa-download fa-fw"></i> Download</a>';
          as_map = '<a class="btn btn-success btn-block hidden-xs" href="' + self.albatross.urls.detail.map.replace('0000', row.id)  + '" data-toggle="tooltip" title="Map"><i class="fa fa-map-marker fa-fw"></i> Map</a>';

          as_text = blank;
          if (row.total < 3000) {
            as_text = '<a class="btn btn-success btn-block" href="' + self.albatross.urls.detail.text.replace('0000', row.id) + '" data-toggle="tooltip" title="Tweet Listing"><i class="fa fa-th-list fa-fw"></i> View</a>';
          }

          as_cloud = blank;
          if (row.cloud_generated && row.total >= 200) {
            as_cloud = '<a class="btn btn-success btn-block hidden-xs" href="' + self.albatross.urls.detail.cloud.replace('0000', row.id) + '" data-toggle="tooltip" title="Word Cloud"><i class="fa fa-cloud fa-fw"></i> Word Cloud</a>';
          }

          as_statistics = blank;
          as_images = blank;
          if (row.statistics_generated) {
            as_statistics = '<a class="btn btn-success btn-block" href="' + self.albatross.urls.detail.statistics.replace('0000', row.id)  + '" data-toggle="tooltip" title="Statistics"><i class="fa fa-pie-chart fa-fw"></i> Statistics</a>';
            as_images = '<a class="btn btn-success btn-block hidden-xs" href="' + self.albatross.urls.detail.images.replace('0000', row.id)  + '" data-toggle="tooltip" title="Images"><i class="fa fa-camera fa-fw"></i> Images</a>';
          }

        } else if (!row.is_running) {

          total = row.total;
          download = not_available;
          as_text = not_available;
          as_cloud = not_available;
          as_statistics = not_available;
          as_map = not_available;

        }

        var now = moment().utc();
        var time = "";

        var started = moment(row.started).utc();
        var stopped = moment(row.stopped).utc();

        var start_time, duration, status;
        if (started > now) {  // Hasn't started yet
          start_time = "Starts: " + started.fromNow();
          duration = "Duration: " + stopped.from(started, true);
          status = "waiting";
        } else {
          if (stopped < now) {  // Has already stopped
            start_time = "Started: " + started.fromNow();
            duration = "Duration: " + stopped.from(started, true);
            status = "stopped";
          } else {
            start_time = "Started: " + started.fromNow();
            duration = "Remaining: " + stopped.fromNow(true);
            status = "running";
          }
        }

        if (!row.stopped) {
          duration = "Never Ending";
        }

        switch (true) {
          case row.stopped >= now:
            time = "Remaining: " + self._getReasonableTime(now, row.stopped);
            break;

        }

        var mine = (self.user_id == row.user_id) ? " mine" : "";

        var $node = $(
          '<div class="grid-item' + mine + ' ' + status + '">' +
            '<div class="node" data-toggle="popover">' +
              '<div class="query">' + query + '</div>' +
              '<div class="time">' + start_time + '</div>' +
              '<div class="time">' + duration + '</div>' +
              '<div class="numeric">' + total + ' tweets, ' + size + '</div>' +
              '<div class="pop-content">' +
                download + as_text + as_cloud + as_statistics + as_images + as_map +
              '</div>' +
            '</div>' +
          '</div>'
        );

        $node.find('[data-toggle="tooltip"]').tooltip();
        self.$archives.append($node);

      }

      var $isotope = $('.grid').isotope({
        itemSelector: '.grid-item',
        //layoutMode: 'fitRows',
        percentPosition: true,
        masonry: {
          columnWidth: '.grid-sizer'
        }
      });

      $('[data-toggle="popover"]').popover({
        html: true,
        placement: "top",
        title: function(){
          return $(this).find(".query").text();
        },
        content: function(){
          return $(this).find(".pop-content").html();
        }
      });
      self.$filters.on( 'click', 'button', function(){
        var $this = $(this);
        $this.siblings().removeClass("active");
        $this.addClass("active");
        $isotope.isotope({
          filter: self.get_filters()
        });
      });

    });

  };

  this.get_filters = function(){
    var possession = self.$filters
      .find(".possession")
      .find("button.active")
      .attr("data-filter");
    var statuses = self.$filters
      .find(".statuses")
      .find("button.active")
      .attr("data-filter");

    if (possession == "*" && statuses == "*") {
      return "*";
    }
    return possession + statuses;
  };

  this.buttonify_select(this.$duration_select);
  this.populate_archives(albatross.urls.api.archives.listing);

  $('#id_start').datetimepicker({
    useCurrent: false,
    format: "YYYY-MM-DD HH:mm:ss",
    minDate: moment()
  });

  return this;

};
