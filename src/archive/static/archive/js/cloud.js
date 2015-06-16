var Cloud = function(albatross, pk){

  var self = this;

  this.albatross = albatross;
  this.pk = pk;

  this.$cloud = $("#cloud");
  this.fill = d3.scale.category20c();

  this.layout = null;
  this.multiplier = 1;
  this._data = null;
  this.url = albatross.urls.api.archives.distillation.cloud.replace(
    '0000',
    this.pk
  );

  // Rebuild the UI to go fullscreen
  $("#global-container").removeClass("container").addClass("col-xs-12");

  this.populate_cloud = function(){

    // Get the width of the space and use it to scale the <canvas>
    var w = this.$cloud.width();
    var h = this.$cloud.width() * 0.5;
    this.multiplier = w / 2100;

    this._get_data(this.url, function(data){
      self.layout = d3.layout.cloud()
        .size([w, h])
        .words(self.strip_down_data(data))
        .padding(3)
        .rotate(function() { return ~~(Math.random() * 2) * 90; })
        .font("Georgia, Times New Roman")
        .fontSize(function(d) { return d.size; })
        .on("end", self.draw);
        self.layout.start();
    });

  };

  this.strip_down_data = function(data){
    var r = [];
    for (var i = 0; i < data.length; i++){
      if (data[i].text == "change") { console.log(data[i]); }
      var size = data[i].size * self.multiplier;
      if (size > 6) {
        data[i].size = size;
        r.push(data[i]);
      }
    }
    return r;
  };

  this._get_data = function(url, callback){
    if (this._data) {
      callback(JSON.parse(JSON.stringify(this._data)));
    } else {
      $.getJSON(url, function(data){
        self._data = data;
        self._get_data(url, callback);
      });
    }
  };

  this.draw = function(words){
    self.$cloud.html("");
    d3.select("#cloud").append("svg")
        .attr("width", self.layout.size()[0])
        .attr("height", self.layout.size()[1])
      .append("g")
        .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
      .selectAll("text")
        .data(words)
      .enter().append("text")
        .style("font-size", function(d) { return d.size + "px"; })
        .style("font-family", "Georgia, 'Times New Roman', Times")
        .style("fill", function(d, i) { return fill(i); })
        .attr("text-anchor", "middle")
        .attr("transform", function(d) {
          return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
        })
        .text(function(d) { return d.text; });
  };

  this.populate_cloud();

  var id;
  $(window).resize(function() {
    clearTimeout(id);
    id = setTimeout(self.populate_cloud, 500);
  });

  return this;

};
