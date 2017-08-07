//=================================== Slide Home =====================================//
if ($('#slide').length)
    $('#slide').camera({
        height: 'auto'
    });

//=================================== Sticky nav ===================================//

$(".mainmenu").sticky({topSpacing:0});

$("#menu").tinyNav();

//=================================== Nav Superfish ===============================//

$('ul.sf-menu').superfish();

$("#events-carousel").owlCarousel({
   autoPlay: 3200,      
   items : 3,
   navigation: false,
   itemsDesktop : [1199,3],
   itemsDesktopSmall : [1024,3],
   itemsTablet: [1000,2],
   itemsMobile : [480,1],
   pagination: true
});

$("#players-carousel").owlCarousel({
       autoPlay: 3200,      
       items : 4,
       navigation: false,
       itemsDesktopSmall : [1024,3],
       itemsTablet : [768,3],
       itemsMobile : [600,2],
       pagination: true
   });
//================================= Smartum carousel ==============================//
$("#support").owlCarousel({
   autoPlay: 3200,
   items : 3,
   navigation: false,
    autoHeight: true,
   itemsDesktop : [1199,4],
   itemsDesktopSmall : [1024,3],
   itemsTablet : [768,3],
   itemsMobile : [500,2],
   pagination: true
});

