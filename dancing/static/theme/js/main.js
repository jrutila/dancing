//=================================== Slide Home =====================================//
if ($('#slide').length)
    $('#slide').camera({
        height: 'auto'
    });

//=================================== Sticky nav ===================================//

$(".mainmenu").sticky({topSpacing:0});

//=================================== Nav Superfish ===============================//

$('ul.sf-menu').superfish();


//================================= Smartum carousel ==============================//
$("#support").owlCarousel({
   autoPlay: 3200,
   items : 6,
   navigation: false,
   itemsDesktop : [1199,5],
   itemsDesktopSmall : [1024,4],
   itemsTablet : [768,3],
   itemsMobile : [500,2],
   pagination: true
});

