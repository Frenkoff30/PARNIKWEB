(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  var desktop = window.matchMedia('(min-width: 900px)');

  var $  = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };

  var rok = $('#rok');
  if (rok) rok.textContent = new Date().getFullYear();

  var reveals = $$('.reveal');
  if (!('IntersectionObserver' in window) || reduced.matches) {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var revealIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var siblings = $$('.reveal', e.target.parentNode);
        var i = siblings.indexOf(e.target);
        e.target.style.transitionDelay = Math.min(i, 6) * 70 + 'ms';
        e.target.classList.add('is-in');
        revealIO.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    reveals.forEach(function (el) { revealIO.observe(el); });
  }

  var burger = $('.burger');
  var menu = $('#menu');
  var lastFocus = null;

  function openMenu() {
    lastFocus = document.activeElement;
    menu.hidden = false;
    document.body.style.overflow = 'hidden';
    requestAnimationFrame(function () { menu.classList.add('is-open'); });
    burger.setAttribute('aria-expanded', 'true');
    burger.setAttribute('aria-label', 'Zavřít menu');
    var first = $('a', menu);
    if (first) first.focus();
  }

  function closeMenu() {
    menu.classList.remove('is-open');
    burger.setAttribute('aria-expanded', 'false');
    burger.setAttribute('aria-label', 'Otevřít menu');
    document.body.style.overflow = '';
    window.setTimeout(function () { menu.hidden = true; }, 240);
    if (lastFocus) lastFocus.focus();
  }

  if (burger && menu) {
    burger.addEventListener('click', function () {
      if (burger.getAttribute('aria-expanded') === 'true') closeMenu(); else openMenu();
    });
    menu.addEventListener('click', function (e) {
      if (e.target === menu || e.target.closest('a')) closeMenu();
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) closeMenu();
    });
    menu.addEventListener('keydown', function (e) {
      if (e.key !== 'Tab') return;
      var f = $$('a, button', menu);
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
  }

  var chapterLinks = $$('.chapters a');
  var chaptersNav = $('.chapters');
  var watched = chapterLinks
    .map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); })
    .filter(Boolean);

  if ('IntersectionObserver' in window && watched.length) {
    var secIO = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        var id = e.target.id;
        chapterLinks.forEach(function (a) {
          a.classList.toggle('is-active', a.getAttribute('href') === '#' + id);
        });
        if (chaptersNav) {
          chaptersNav.classList.toggle('on-light',
            e.target.classList.contains('section--day') || e.target.classList.contains('section--light'));
        }
      });
    }, { rootMargin: '-45% 0px -45% 0px', threshold: 0 });
    watched.forEach(function (s) { secIO.observe(s); });
  }

  var railFill = $('.rail__fill');
  var railBoat = $('.rail__boat');
  var bridge = $('#bridge');
  var route = $('.route');
  var routePan = $('.route__pan');
  var routeStops = $$('.route__stops li');
  var routeProg = $('.route__prog span');

  var ticking = false;
  var lastStop = -1;
  var panShift = 0;

  function measure() {
    if (!route || !routePan) return;
    var stage = $('.route__stage');
    if (!stage) return;
    panShift = Math.max(0, routePan.offsetWidth - stage.offsetWidth);
  }

  function frame() {
    ticking = false;
    var y = window.pageYOffset || document.documentElement.scrollTop;
    var docH = document.documentElement.scrollHeight - window.innerHeight;
    var p = docH > 0 ? clamp(y / docH, 0, 1) : 0;

    if (railFill) railFill.style.transform = 'scaleX(' + p + ')';
    if (railBoat) railBoat.style.transform = 'translateX(calc(' + (p * 100) + 'vw - 50%))';
    if (bridge) bridge.classList.toggle('is-stuck', y > 40);

    if (route && routePan && desktop.matches && !reduced.matches) {
      var top = route.offsetTop;
      var span = route.offsetHeight - window.innerHeight;
      var rp = span > 0 ? clamp((y - top) / span, 0, 1) : 0;

      routePan.style.transform = 'translate3d(' + (-panShift * rp) + 'px,0,0)';
      if (routeProg) routeProg.style.width = (rp * 100) + '%';

      var idx = 0;
      for (var i = 0; i < routeStops.length; i++) {
        if (parseFloat(routeStops[i].dataset.at) <= rp + 0.04) idx = i;
      }
      if (idx !== lastStop) {
        routeStops.forEach(function (li, i) { li.classList.toggle('is-on', i === idx); });
        lastStop = idx;
      }
    }
  }

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(frame);
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', function () { measure(); onScroll(); }, { passive: true });
  window.addEventListener('load', function () { measure(); onScroll(); });
  measure();
  onScroll();

  var form = $('#poptavka');
  if (form) {
    var status = $('.form__status', form);
    var EMAIL = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;

    function setError(field, msg) {
      var wrap = field.closest('.field');
      var slot = $('[data-err-for="' + field.id + '"]', wrap) || $('[data-err-for="' + field.id + '"]', form);
      if (wrap) wrap.classList.toggle('is-bad', !!msg);
      if (slot) slot.textContent = msg || '';
      field.setAttribute('aria-invalid', msg ? 'true' : 'false');
      return !msg;
    }

    function validate(field) {
      var v = (field.value || '').trim();

      if (field.type === 'checkbox') {
        return setError(field, field.checked ? '' : 'Bez souhlasu bohužel nemůžeme poptávku zpracovat.');
      }
      if (field.required && !v) {
        return setError(field, 'Toto pole prosím vyplňte.');
      }
      if (field.type === 'email' && v && !EMAIL.test(v)) {
        return setError(field, 'Zkontrolujte prosím formát e-mailu.');
      }
      if (field.id === 'telefon' && v && v.replace(/[^\d]/g, '').length < 9) {
        return setError(field, 'Telefon vypadá příliš krátce.');
      }
      if (field.id === 'osoby' && v && (+v < 1 || +v > 300)) {
        return setError(field, 'Zadejte počet 1 až 300 osob.');
      }
      if (field.id === 'datum' && v) {
        var dnes = new Date(); dnes.setHours(0, 0, 0, 0);
        if (new Date(v) < dnes) return setError(field, 'Termín nemůže být v minulosti.');
      }
      return setError(field, '');
    }

    var fields = $$('input, select, textarea', form);
    fields.forEach(function (f) {
      f.addEventListener('blur', function () { validate(f); });
      f.addEventListener('input', function () {
        if (f.closest('.field').classList.contains('is-bad')) validate(f);
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = true;
      var firstBad = null;
      fields.forEach(function (f) {
        if (!validate(f)) { ok = false; if (!firstBad) firstBad = f; }
      });

      if (!ok) {
        status.textContent = 'Zkontrolujte prosím označená pole.';
        status.style.color = '#F0A79B';
        if (firstBad) firstBad.focus();
        return;
      }

      var btn = $('button[type="submit"]', form);
      btn.disabled = true;
      btn.textContent = 'Odesíláme…';
      status.style.color = '';
      status.textContent = '';

      /* TODO: napojit na endpoint, viz README */
      window.setTimeout(function () {
        btn.disabled = false;
        btn.textContent = 'Odeslat nezávaznou poptávku';
        status.style.color = '';
        status.textContent = 'Děkujeme, poptávku máme. Ozveme se do 24 hodin, nejpozději následující pracovní den.';
        form.reset();
        fields.forEach(function (f) { setError(f, ''); });
      }, 900);
    });
  }

  function resetRoute() {
    if (!routePan) return;
    if (!desktop.matches || reduced.matches) {
      routePan.style.transform = '';
      routeStops.forEach(function (li) { li.classList.remove('is-on'); });
      lastStop = -1;
    } else {
      measure();
      onScroll();
    }
  }
  if (desktop.addEventListener) desktop.addEventListener('change', resetRoute);
  if (reduced.addEventListener) reduced.addEventListener('change', resetRoute);
})();
