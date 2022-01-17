// Hello, world!

(function () {
    document.querySelector('main').addEventListener('click', function (event) {
        if (event.target.tagName == 'A') {
            var href = event.target.href;

            if (href && href.startsWith('gemini://')) {
                event.preventDefault();
                event.stopPropagation();
                window.location.assign('/' + href.substring(9));
            } else if (href) {
                // Ensure it isn't an absolute URL.
                // However, event.target.href will have been resolved at this point,
                // so we check the original attribute value...
                var originalHref = event.target.getAttribute('href');
                if (originalHref.startsWith('/')) {
                    var currentPath = window.location.pathname;
                    var slashIndex = currentPath.indexOf('/', 1);
                    event.preventDefault();
                    event.stopPropagation();
                    window.location.assign(currentPath.substring(0, slashIndex) + originalHref);
                }
            }
        }
    });
})();
