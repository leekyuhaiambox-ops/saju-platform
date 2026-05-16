// 사주명리 플랫폼 클라이언트 스크립트

// ─── 글로벌 공유 함수 (template에서 onclick 호출) ───
function copyLink(btn) {
  if (!navigator.clipboard) {
    prompt('이 링크를 복사하세요:', location.href);
    return;
  }
  navigator.clipboard.writeText(location.href).then(function () {
    var original = btn.textContent;
    btn.textContent = '링크 복사됨 ✓';
    setTimeout(function () { btn.textContent = original; }, 2000);
  });
}

function shareKakao() {
  // 카카오 SDK가 있으면 SDK 사용, 없으면 카카오톡 share URL로 폴백
  if (window.Kakao && window.Kakao.Share) {
    var ogImage = document.querySelector('meta[property="og:image"]')?.content || '';
    window.Kakao.Share.sendDefault({
      objectType: 'feed',
      content: {
        title: document.title,
        description: document.querySelector('meta[name="description"]')?.content || '',
        imageUrl: ogImage,
        link: { mobileWebUrl: location.href, webUrl: location.href },
      },
      buttons: [{ title: '내 사주 보러가기', link: { mobileWebUrl: location.href, webUrl: location.href } }],
    });
  } else {
    // Web Share API fallback (모바일 카카오톡에서 작동)
    if (navigator.share) {
      navigator.share({ title: document.title, url: location.href }).catch(function () {});
    } else {
      copyLink({ textContent: '링크 복사' });
      alert('카카오톡으로 공유하려면 링크를 카카오톡에 붙여넣으세요.');
    }
  }
  if (window.fbq) fbq('trackCustom', 'Share', { platform: 'kakao' });
}

(function () {
  'use strict';

  // 폼 제출 시 로딩 UI 표시
  var form = document.getElementById('sajuForm');
  if (form) {
    form.addEventListener('submit', function () {
      var btn = form.querySelector('.cta-button');
      if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<span class="cta-main">사주를 분석하는 중...</span><span class="cta-sub">잠시만 기다려 주세요</span>';
      }
      if (window.fbq) fbq('track', 'Lead');
    });
  }

  // 결과 페이지의 막대 그래프 페이드인
  document.querySelectorAll('.bar-fill').forEach(function (b) {
    var w = b.style.width;
    b.style.width = '0%';
    setTimeout(function () { b.style.width = w; }, 100);
  });

  // 외부 링크 _blank 자동 보안 속성
  document.querySelectorAll('a[target="_blank"]').forEach(function (a) {
    if (!a.rel.includes('noopener')) a.rel = (a.rel + ' noopener').trim();
  });

  // 일주 상세 페이지 키보드 네비
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    var prev = document.querySelector('.pillar-nav a:nth-child(1)');
    var next = document.querySelector('.pillar-nav a:nth-child(3)');
    if (e.key === 'ArrowLeft' && prev) location.href = prev.href;
    if (e.key === 'ArrowRight' && next) location.href = next.href;
  });
})();
