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
   itemsDesktop : [1199,5],
   itemsDesktopSmall : [1024,4],
   itemsTablet : [768,3],
   itemsMobile : [500,2],
   pagination: true
});

