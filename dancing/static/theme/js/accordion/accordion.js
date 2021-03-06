
    (function() {

    var $container = $('.acc-container'),
      $trigger   = $('.acc-trigger'),
      $startActives = $('.acc-trigger.active');

    $container.hide();
    //$trigger.first().addClass('active').next().show();
    $startActives.next().show();

    var fullWidth = $container.outerWidth(true);
    $trigger.css('width', fullWidth);
    $container.css('width', "100%");
    
    $trigger.on('click', function(e) {
      if( $(this).next().is(':hidden') ) {
        //$trigger.removeClass('active').next().slideUp(300);
        $(this).toggleClass('active').next().slideDown(300);
      } else {
        $(this).toggleClass('active').next().slideUp(300);
      }
      e.preventDefault();
    });

    // Resize
    $(window).on('resize', function() {
      fullWidth = $container.outerWidth(true)
      $trigger.css('width', $trigger.parent().width() );
      $container.css('width', $container.parent().width() );
    });

  })();