document.addEventListener('DOMContentLoaded', async () => {
    // ===== 1) Collapse «читать далее» =====
    const collapseEl = document.getElementById('fullDesc');
    const toggleBtn  = document.getElementById('toggleDescBtn');
    if (collapseEl && toggleBtn) {
        collapseEl.addEventListener('show.bs.collapse', () => toggleBtn.textContent = 'Скрыть');
        collapseEl.addEventListener('hide.bs.collapse', () => toggleBtn.textContent = '…читать далее');
    }

    // ===== 2) Загрузка и отображение событий в обычной Bootstrap-карусели =====

        $(document).ready(async function () {
        try {
        const response = await fetch('/api/events.php');
        const events = await response.json();

        const $slider = $('#eventSlider');

        events.forEach(event => {
        const slide = `
                <div class="card h-100 shadow-sm rounded-4 overflow-hidden mx-2">
                    <img src="static/img/events/${event.image}" class="card-img-top" style="object-fit: cover;" alt="${event.title}">
                    <div class="event-caption text-white">
                        <h5 class="card-title">${event.title}</h5>
                        ${event.description ? `<p class="card-text">${event.description}</p>` : ''}
                    </div>
                </div>
            `;
        $slider.append(slide);
    });

        $slider.owlCarousel({
        loop: true,
        margin: 12,
        nav: true,
        dots: true,
        autoplay: false,
        smartSpeed: 500,
        responsive: {
            0:    { items: 1 },
            768:  { items: 2 },
            1200: { items: 3 }
    },
        navText: [
        '<span class="btn btn-light rounded-circle shadow"><</span>',
        '<span class="btn btn-light rounded-circle shadow">></span>'
        ]
    });

    } catch (e) {
        console.error('Ошибка загрузки событий:', e);
    }
    });



    // ===== 3) Загрузка и отображение преподавателей =====
    // ===== 3) Загрузка и отображение преподавателей через Swiper =====
    const tCont = document.getElementById('teachersContainer');
    tCont.innerHTML = '';
    for (let i = 0; i < 3; i++) {
        const slide = document.createElement('div');
        slide.className = 'swiper-slide';
        slide.innerHTML = `
    <div class="d-flex flex-md-row flex-column align-items-center justify-content-md-start justify-content-center
                p-3 shadow-lg rounded-4 border"
         style="background: linear-gradient(to right, #ffffff, #f9fbff); border: 1px solid rgba(0, 0, 0, 0.08); gap: 1.5rem; min-height: 240px;">
      
      <div class="skeleton" style="width: 140px; height: 180px; border-radius: 1rem; background: #bab6b6;"></div>

      <div class="w-100">
        <div class="skeleton mb-2" style="width: 60%; height: 20px; border-radius: 4px;"></div>
        <div class="skeleton mb-2" style="width: 40%; height: 16px; border-radius: 4px;"></div>
        <div class="skeleton" style="width: 50%; height: 16px; border-radius: 4px;"></div>
      </div>
    </div>
  `;
        tCont.appendChild(slide);
    }
    try {
        const respT = await fetch('/api/teachers.php');
        const teachers = await respT.json();
        console.log('Преподаватели:', teachers);

        tCont.innerHTML = '';

        teachers.forEach(t => {
            const slide = document.createElement('div');
            slide.className = 'swiper-slide';
            slide.innerHTML = `
<div class="swiper-slide">
  <div class="d-flex flex-md-row flex-column align-items-center justify-content-md-start justify-content-center
              p-3 shadow-lg rounded-4 border"
       style="
         background: linear-gradient(to right, #ffffff, #f9fbff);
         border: 1px solid rgba(0, 0, 0, 0.08);
         gap: 1.5rem;
         min-height: 240px;
         transition: transform 0.3s ease, box-shadow 0.3s ease;
       "
       onmouseover="this.style.transform='scale(1.01)'; this.style.boxShadow='0 12px 32px rgba(0,0,0,0.1)'"
       onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 6px 12px rgba(0,0,0,0.08)'">

    <img src="static/img/teachers/${t.photo}" alt="${t.name}"
         class="img-fluid rounded-4 shadow-sm"
         style="width: 140px; height: 180px; object-fit: cover; border: 3px solid #e0e0e0;" />

    <div class="text-md-start text-center">
      <h5 class="fw-bold">${t.name}</h5>
      <p class="mb-1 text-muted">${t.position}</p>
      <p class="text-secondary">Опыт: ${t.experience} года</p>
      ${t.link ? `<a href="${t.link}" class="btn btn-outline-primary btn-sm mt-2" target="_blank">Профиль</a>` : ''}
    </div>
  </div>
</div>
  `;
            tCont.appendChild(slide);
        });

        // Инициализация Swiper
        const swiper = new Swiper('.mySwiper', {
            slidesPerView: 1,
            spaceBetween: 30,
            slidesPerGroup: 1,
            loop: false,
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            breakpoints: {
                576: { slidesPerView: 1 },
                768: { slidesPerView: 2 },
                992: { slidesPerView: 3 }
            }
        });

    } catch (e) {
        console.error('Ошибка загрузки преподавателей:', e);
    }


    // ===== 4) Копирование телефона =====
    document.querySelectorAll('.copy-phone').forEach(el => {
        el.addEventListener('click', () => {
            const text = el.dataset.phone;
            navigator.clipboard.writeText(text).then(() => {
                el.textContent = 'Скопировано!';
                el.style.color = 'green';
                setTimeout(() => {
                    el.textContent = text;
                    el.style.color = '';
                }, 1500);
            });
        });
    });

    // ===== 5) Reveal on scroll =====
    function revealOnScroll() {
        document.querySelectorAll('.reveal').forEach(el => {
            if (el.getBoundingClientRect().top < window.innerHeight - 100) {
                el.classList.add('active');
            }
        });
    }
    window.addEventListener('scroll', revealOnScroll);
    window.addEventListener('load', revealOnScroll);

    // ===== 6) IntersectionObserver для .fade-in-on-view =====
    const observer = new IntersectionObserver((entries, obs) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                obs.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });
    document.querySelectorAll('.fade-in-on-view')
        .forEach(el => observer.observe(el));

    // ===== 7) Анимация hero-content =====
    const hero = document.querySelector('.hero-content');
    if (hero) setTimeout(() => hero.classList.add('visible'), 100);
});
