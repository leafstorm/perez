// Intercepts gemini:// and host-relative links so they use the proxy.
//
// Copyright (C) 2022 Matthew Frazier
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions
// are met:
//
// 1. Redistributions of source code must retain the above copyright
//    notice, this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
//    notice, this list of conditions and the following disclaimer in the
//    documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
//    contributors may be used to endorse or promote products derived from
//    this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
// TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
// PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
// LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
// NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
// SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
