//$(function(){
//  $('.minimized').click(function(event) {
//    var i_path = $(this).attr('src');
//    $('body').append('<div id="overlay"></div><div id="magnify"><img src="'+i_path+'"><div id="close-popup"><i></i></div></div>');
//    $('#magnify').css({
//     left: ($(document).width() - $('#magnify').outerWidth())/2,
//     // top: ($(document).height() - $('#magnify').outerHeight())/2 upd: 24.10.2016
//            top: ($(window).height() - $('#magnify').outerHeight())/2
//   });
//    $('#overlay, #magnify').fadeIn('fast');
//  });
//
//  $('body').on('click', '#close-popup, #overlay', function(event) {
//    event.preventDefault();
//
//    $('#overlay, #magnify').fadeOut('fast', function() {
//      $('#close-popup, #magnify, #overlay').remove();
//    });
//  });
//});

//window.onload = function(){
//var image = document.getElementById('mask'), even = true, imageWidth = image.clientWidth, imageHeight = image.clientHeight;
//image.onclick = function(){
//  if (even) {
//     this.style.width = imageWidth * 4 + "px";
//     this.style.height = imageHeight * 4 + "px";
//     even = false;
//  } else {
//     this.style.width = imageWidth + "px";
//     this.style.height = imageHeight + "px";
//     even = true;
//  }
//}
//};

window.onload = function(){
    var id_images = ['mask','trajectory'], image, even = true, imageWidth;
    for(var i=0; i< id_images.length; i++){
        image = document.getElementById(id_images[i]);
        imageWidth = image.clientWidth;

        image.onclick = function(even, imageWidth){
        return function(){
            if (even) {
                even = false;
                this.style.width = outerWidth + "px";
            } else {
                this.style.width = imageWidth + "px";
                even = true;
            }
        }
        }(even,imageWidth);
    }
};
