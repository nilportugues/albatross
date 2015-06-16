/*
 *
 * Ad blockers are really getting out of control if naming a file "statistics"
 * is going to get it removed from the DOM.
 *
 * Still to do... maybe
 * ???: most rt'd user
 *
 */
var Statistics = function(albatross, pk, query, colour_overrides, events){

  var self = this;

  this.colour_overrides = colour_overrides || {};
  this.events = events || [];

  this.albatross = albatross;
  this.pk = pk;
  this.query = query;

  this.loading = '' +
    '<i class="fa fa-spin fa-cog fa-fw" style="font-size: xx-large"></i>' +
    '<span style="font-size: large;">' +
      'Loading &nbsp; ' +
      '<small>(Large data sets may slow things down... a lot.)</small>' +
    '</span>';

  this.$languages = $("#languages");
  this.$hashtags = $("#hashtags");
  this.$mentions = $("#mentions");
  this.$countries = $("#countries");
  this.$sentiments = $("#sentiments");
  this.$hours = $("#hours");
  this.$makeup = $("#makeup");

  this.$simple = $("#simple-table");

  this.$map = $("#map");

  this.populate_statistics = function(){

    var url = self.albatross.urls.api.archives.distillation.statistics.replace(
      '0000', this.pk);

    $.getJSON(url, function(data) {

      self.make_pie("Languages", self.$languages, data.languages);
      self.make_pie("Hashtags", self.$hashtags, data.hashtags);
      self.make_pie("Mentions", self.$mentions, data.mentions);
      self.make_pie("Countries", self.$countries, data.countries.pie);
      self.make_pie("Makeup", self.$makeup, data.makeup);

      self.make_pie("Sentiment (Beta)", self.$sentiments, data.sentiments, {
        "Positive": "#2ca02c", "Negative": "#d62728", "Neutral": "#7f7f7f"});

      self.draw_hours(self.$hours, data.hours);

      //self.draw_simple(self.$simple, data.urls, data.images);

      self.draw_map(self.$map, data.countries.complete);

    });

  };

  this.make_pie = function(name, $target, data, colour_overrides){

    var width = $target.width();

    if (data[data.length - 1][0] == "*") {
      data[data.length - 1][0] = "Other";
    }

    if (!colour_overrides) {
      colour_overrides = self.colour_overrides[name.toLowerCase()] || {};
    }

    //noinspection JSSuspiciousNameCombination
    c3.generate({
      bindto: $target.selector,
      data: {
        columns: data,
        type : 'donut',
        colors: colour_overrides
      },
      donut: {
        title: name
      },
      size: {
        width: width,
        height: width
      },
      tooltip: {
        format: {
          name: function (name, ratio, id, index) {
            return name + " (" + data[index][1] + ")";
          }
        }
      }
    });

  };

  this.draw_hours = function($target, hours){

    var graph_type = (hours.data.length < 100) ? "bar": "area-spline";
    // Some datasets are just too big, so we grab the last n records
    var subsets = {
        times: hours.times.slice(hours.times.length - 300, hours.times.length),
        data: hours.data.slice(hours.data.length - 300, hours.data.length)
    };

    subsets.times = hours.times;
    subsets.data = hours.data;

    var times = ["x"].concat($.map(subsets.times, function(__){
        return new Date(__);
    }));
    var data = [this.query].concat(subsets.data);

    var time_count = times.length;

    this.hours_chart = c3.generate({
      bindto: $target.selector,
      data: {
        x: "x",
        columns: [times, data],
        type: graph_type
      },
      axis: {
        x: {
          type: 'timeseries',
          tick: {
            format: function(t){
              if (time_count < 25) {
                return moment(t).format("hA");
              }
              return moment(t).format("MMM DD");
            },
            culling: {
              max: ($(window).width() < 500) ? 5 : 10
            }
          }
        }
      },
      subchart: {
        show: true
      },
      zoom: {
        enabled: true
      },
      grid: {
        x: {
          lines: self.events
        },
        y: {
          show: false
        }
      },
      point: {
        show: false
      },
      tooltip: {
        format: {
          title: function (d){
              return d;
          }
        }
      }
    });

  };

  this.draw_simple = function($target, urls, images){
    var $table = $('<table class="table table-responsive table-hover"></table>');
    $table
      .append('<tr><th>URLs</th><td>' + urls + '</td></tr>')
      .append('<tr><th>Images</th><td>' + Object.keys(images).length + '</td></tr>');
    $target.append($table);
  };

  this.draw_map = function($target, data){
    $target.vectorMap({
      map: 'world_en',
      borderColor: "#999",
      backgroundColor: null,
      color: '#7a7c7f',
      hoverOpacity: 0.7,
      selectedColor: '#666666',
      enableZoom: true,
      showTooltip: true,
      values: data,
      scaleColors: ['#b8d2eb', '#1859a9'],
      normalizeFunction: 'polynomial',
      onLabelShow: function(element, label, code){
        var total = data[code];
        if (total) {
          label[0].innerHTML += ": " + total;
        }
      }
    });
  };

  this.populate_statistics();

  return this;

};
