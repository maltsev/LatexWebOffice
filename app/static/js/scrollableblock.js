$(function () {
    var $document = $(document),
        $scrollableBlock = $(".scrollableblock:first");
    if (! $scrollableBlock.length) {
        return;
    }

    var $dummy = $("<div>").hide()
        navbarHeight = $("#navbar").height();

    $scrollableBlock.after($dummy);

    $(window).scroll(function () {
        var documentScrollTop = $document.scrollTop(),
            isFixed = $scrollableBlock.hasClass("scrollableblock-fixed"),
            $foo = isFixed ? $dummy : $scrollableBlock;

        if (documentScrollTop + navbarHeight >= $foo.offset().top) {
            if (! isFixed) {
                $scrollableBlock.css({
                    "top": navbarHeight,
                    "width": $scrollableBlock.width()
                }).addClass("scrollableblock-fixed");
                $dummy.height($scrollableBlock.outerHeight(true)).show();
            }
        } else {
            if (isFixed) {
                $scrollableBlock.removeClass("scrollableblock-fixed").css("width", "auto");
                $dummy.hide();
            }
        }
    });
});