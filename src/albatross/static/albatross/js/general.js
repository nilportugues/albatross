var Albatross = function(urls){

  this.urls = urls;

  this.fallback_image = function(preferred){
    var fallback = 'https://abs.twimg.com/sticky/default_profile_images/default_profile_4_normal.png';
    return '<img src="' + preferred + '" onerror="if (this.src !== \'' + fallback + '\') this.src = \'' + fallback + '\';" class="img-responsive">';
  };

  return this;

};
