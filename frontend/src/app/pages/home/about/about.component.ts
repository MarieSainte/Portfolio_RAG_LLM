import { Component } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [TranslateModule],
  template: `
    <section class="section about">
      <div class="container">
        <div class="about__inner">
          <!-- Left: Text -->
          <div class="about__content">
            <span class="section-header__tag" style="margin-bottom:16px; display:inline-block">
              {{ 'HOME.ABOUT.TAG' | translate }}
            </span>
            <h2 class="about__title">{{ 'HOME.ABOUT.TITLE' | translate }}</h2>
            <p>{{ 'HOME.ABOUT.TEXT_1' | translate }}</p>
            <p>{{ 'HOME.ABOUT.TEXT_2' | translate }}</p>
            <p>{{ 'HOME.ABOUT.TEXT_3' | translate }}</p>
            <a href="#" class="btn btn--primary about__cta">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              {{ 'HOME.ABOUT.DOWNLOAD_CV' | translate }}
            </a>
          </div>

          <!-- Right: Info card -->
          <div class="about__card">
            <div class="info-card">
              <div class="info-card__header">
                <div class="info-card__dots"><span></span><span></span><span></span></div>
                <span class="info-card__title">profile.json</span>
              </div>
              <pre class="info-card__code"><span class="c-bracket">&#123;</span>
  <span class="c-key">"role"</span><span class="c-punct">:</span> <span class="c-string">"Ingénieur IA"</span><span class="c-punct">,</span>
  <span class="c-key">"status"</span><span class="c-punct">:</span> <span class="c-string">"Junior"</span><span class="c-punct">,</span>
  <span class="c-key">"experience"</span><span class="c-punct">:</span> <span class="c-string">"5 ans Support IT"</span><span class="c-punct">,</span>
  <span class="c-key">"location"</span><span class="c-punct">:</span> <span class="c-string">"France 🇫🇷"</span><span class="c-punct">,</span>
  <span class="c-key">"languages"</span><span class="c-punct">:</span> <span class="c-bracket">&#123;</span>
    <span class="c-key">"Français"</span><span class="c-punct">:</span> <span class="c-string">"Natif"</span><span class="c-punct">,</span>
    <span class="c-key">"Anglais"</span><span class="c-punct">:</span> <span class="c-string">"B1"</span>
  <span class="c-bracket">&#125;</span><span class="c-punct">,</span>
  <span class="c-key">"interests"</span><span class="c-punct">:</span> <span class="c-bracket">[</span>
    <span class="c-string">"LLM"</span><span class="c-punct">,</span>
    <span class="c-string">"Computer Vision"</span><span class="c-punct">,</span>
    <span class="c-string">"MLOps"</span>
  <span class="c-bracket">]</span><span class="c-punct">,</span>
  <span class="c-key">"open_to_work"</span><span class="c-punct">:</span> <span class="c-bool">true</span>
<span class="c-bracket">&#125;</span></pre>
            </div>
          </div>
        </div>
      </div>
    </section>
  `,
  styleUrl: './about.component.scss',
})
export class AboutComponent {}
