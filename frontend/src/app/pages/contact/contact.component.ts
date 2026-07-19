import { Component } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

type FormStatus = 'idle' | 'sending' | 'success' | 'error';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [TranslateModule, CommonModule, FormsModule],
  template: `
    <div class="page-enter contact-page">
      <div class="container">
        <div class="contact-grid" style="padding-top: 100px">
          <!-- Form -->
          <div class="contact-form-wrapper">
            <form class="contact-form" (ngSubmit)="onSubmit()" #f="ngForm">
              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">{{ 'CONTACT.FORM.NAME' | translate }}</label>
                  <input
                    type="text"
                    name="name"
                    [(ngModel)]="form.name"
                    required
                    class="form-input"
                    [placeholder]="'CONTACT.FORM.NAME_PLACEHOLDER' | translate"
                  />
                </div>
                <div class="form-group">
                  <label class="form-label">{{ 'CONTACT.FORM.EMAIL' | translate }}</label>
                  <input
                    type="email"
                    name="email"
                    [(ngModel)]="form.email"
                    required
                    class="form-input"
                    [placeholder]="'CONTACT.FORM.EMAIL_PLACEHOLDER' | translate"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">{{ 'CONTACT.FORM.SUBJECT' | translate }}</label>
                <input
                  type="text"
                  name="subject"
                  [(ngModel)]="form.subject"
                  class="form-input"
                  [placeholder]="'CONTACT.FORM.SUBJECT_PLACEHOLDER' | translate"
                />
              </div>

              <div class="form-group">
                <label class="form-label">{{ 'CONTACT.FORM.MESSAGE' | translate }}</label>
                <textarea
                  name="message"
                  [(ngModel)]="form.message"
                  required
                  rows="6"
                  class="form-input form-textarea"
                  [placeholder]="'CONTACT.FORM.MESSAGE_PLACEHOLDER' | translate"
                ></textarea>
              </div>

              <!-- Status messages -->
              @if (status === 'success') {
                <div class="form-alert form-alert--success">
                  ✅ {{ 'CONTACT.FORM.SUCCESS' | translate }}
                </div>
              }
              @if (status === 'error') {
                <div class="form-alert form-alert--error">
                  ❌ {{ 'CONTACT.FORM.ERROR' | translate }}
                </div>
              }

              <button
                type="submit"
                class="btn btn--primary form-submit"
                [disabled]="status === 'sending'"
              >
                @if (status !== 'sending') {
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <line x1="22" y1="2" x2="11" y2="13" />
                    <polygon points="22 2 15 22 11 13 2 9 22 2" />
                  </svg>
                  {{ 'CONTACT.FORM.SEND' | translate }}
                } @else {
                  <span class="spinner"></span>
                  {{ 'CONTACT.FORM.SENDING' | translate }}
                }
              </button>
            </form>
          </div>

          <!-- Info panel -->
          <div class="contact-info">
            <div class="info-section">
              <h3>{{ 'CONTACT.INFO.TITLE' | translate }}</h3>

              <div class="info-item">
                <div class="info-item__icon">📧</div>
                <div>
                  <span class="info-item__label">{{ 'CONTACT.INFO.EMAIL_LABEL' | translate }}</span>
                  <p class="info-item__value">jordan.mariesainte&#64;gmail.com</p>
                </div>
              </div>

              <div class="info-item">
                <div class="info-item__icon">📍</div>
                <div>
                  <span class="info-item__label">{{
                    'CONTACT.INFO.LOCATION_LABEL' | translate
                  }}</span>
                  <p class="info-item__value">{{ 'CONTACT.INFO.LOCATION_VALUE' | translate }}</p>
                </div>
              </div>

              <div class="info-item">
                <div class="info-item__icon">💼</div>
                <div>
                  <span class="info-item__label">{{
                    'CONTACT.INFO.AVAILABILITY' | translate
                  }}</span>
                  <p class="info-item__value availability">
                    <span class="availability-dot"></span>
                    {{ 'CONTACT.INFO.AVAILABILITY_VALUE' | translate }}
                  </p>
                </div>
              </div>
            </div>

            <div class="info-section">
              <h3>{{ 'CONTACT.SOCIAL.TITLE' | translate }}</h3>
              <div class="social-links">
                <a
                  href="https://github.com/MarieSainte"
                  target="_blank"
                  rel="noopener"
                  class="social-link"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                    <path
                      d="M12 2C6.477 2 2 6.477 2 12c0 4.418 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.342-3.369-1.342-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"
                    />
                  </svg>
                  GitHub
                </a>
                <a
                  href="https://www.linkedin.com/in/jordan-marie-sainte-039616b1"
                  target="_blank"
                  rel="noopener"
                  class="social-link"
                >
                  <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                    <path
                      d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"
                    />
                  </svg>
                  LinkedIn
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styleUrl: './contact.component.scss',
})
export class ContactComponent {
  form = { name: '', email: '', subject: '', message: '' };
  status: FormStatus = 'idle';

  onSubmit(): void {
    if (!this.form.name || !this.form.email || !this.form.message) return;
    this.status = 'sending';

    // Simulation envoi — à remplacer par un vrai service
    setTimeout(() => {
      this.status = 'success';
      this.form = { name: '', email: '', subject: '', message: '' };
      setTimeout(() => (this.status = 'idle'), 4000);
    }, 1500);
  }
}
