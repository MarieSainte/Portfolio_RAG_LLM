import { Component, HostListener, ViewChild, ElementRef, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { TranslateModule } from '@ngx-translate/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-hero',
  standalone: true,
  imports: [RouterLink, TranslateModule, FormsModule, CommonModule],
  template: `
    <section class="hero" [style.--mx]="mouseX" [style.--my]="mouseY">
      <div class="container">
        <div class="hero__content">
          <div class="hero__text">
            <div class="hero__greeting animate-fade-in-up">
              <span class="hero__line"></span>
              {{ 'HOME.HERO.GREETING' | translate }}
            </div>

            <h1 class="hero__name animate-fade-in-up delay-100">
              {{ 'HOME.HERO.NAME' | translate }}
            </h1>

            <div class="hero__title-wrapper animate-fade-in-up delay-200">
              <span class="hero__title-prefix">&lt;</span>
              <span class="hero__title">{{ 'HOME.HERO.TITLE' | translate }}</span>
              <span class="hero__title-prefix">/&gt;</span>
            </div>

            <p class="hero__subtitle animate-fade-in-up delay-300">
              {{ 'HOME.HERO.SUBTITLE' | translate }}
            </p>

            <div class="hero__actions animate-fade-in-up delay-400">
              <a routerLink="/projects" class="btn btn--primary">
                {{ 'HOME.HERO.CTA_PROJECTS' | translate }}
              </a>
              <a routerLink="/contact" class="btn btn--outline">
                {{ 'HOME.HERO.CTA_CONTACT' | translate }}
              </a>
            </div>

            <!-- Stats -->
            <div class="hero__stats animate-fade-in-up delay-500">
              <div class="stat">
                <span class="stat__number">5+</span>
                <span class="stat__label">Projets</span>
              </div>
              <div class="stat__divider"></div>
              <div class="stat">
                <span class="stat__number">2</span>
                <span class="stat__label">Ans de formation</span>
              </div>
              <div class="stat__divider"></div>
              <div class="stat">
                <span class="stat__number">∞</span>
                <span class="stat__label">Curiosité</span>
              </div>
            </div>
          </div>

          <!-- Robot Visual -->
          <div class="hero__visual animate-fade-in delay-300">
            <div class="robot" [class.robot--active]="isChatActive">
              <div class="robot__head-wrapper">
                <div class="robot__head">
                  <div class="robot__face">
                    <div class="robot__eyes">
                      <div class="robot__eye"></div>
                      <div class="robot__eye"></div>
                    </div>
                    <div class="robot__blush robot__blush--left"></div>
                    <div class="robot__blush robot__blush--right"></div>
                  </div>
                </div>
                <div class="robot__ear robot__ear--left"></div>
                <div class="robot__ear robot__ear--right"></div>

                <!-- Removed Vision Lens (Request: 100% Text) -->
              </div>
              <div class="robot__neck"></div>
              <div class="robot__body">
                <div class="robot__chest">
                  <button
                    class="robot__connect-btn"
                    (click)="toggleChat()"
                    [class.robot__connect-btn--active]="isChatActive"
                  >
                    <span class="robot__connect-glow"></span>
                    <i class="icon">{{ isChatActive ? '●' : 'Connect' }}</i>
                  </button>
                </div>
              </div>
              <div class="robot__shadow"></div>

              <!-- Chat Overlay (Now inside the robot for better tracking) -->
              @if (isChatActive) {
                <div class="chat-overlay animate-fade-in">
                  <div class="chat-window">
                    <div class="chat-header">
                      <div class="chat-status">
                        <span class="status-dot animate-pulse"></span>
                        {{ 'HOME.HERO.CHAT.STATUS' | translate }}
                      </div>
                      <button class="chat-close" (click)="toggleChat()">×</button>
                    </div>

                    <div class="chat-messages" #scrollContainer>
                      @for (msg of messages; track $index) {
                        <div class="message" [class.message--user]="msg.sender === 'user'">
                          <div class="message-bubble">
                            {{ msg.isKey ? (msg.text | translate) : msg.text }}
                          </div>
                        </div>
                      }
                      @if (isTyping) {
                        <div class="message message--bot">
                          <div class="message-bubble typing-dots">
                            <span></span><span></span><span></span>
                          </div>
                        </div>
                      }
                    </div>

                    <div class="chat-input-wrapper">
                      <input
                        [ngModel]="userInput"
                        (ngModelChange)="userInput = $event"
                        (keyup.enter)="sendMessage()"
                        [placeholder]="'HOME.HERO.CHAT.PLACEHOLDER' | translate"
                        class="chat-input"
                      />
                      <button (click)="sendMessage()" class="chat-send">
                        <svg
                          width="18"
                          height="18"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                        >
                          <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
                        </svg>
                      </button>
                    </div>

                    <!-- Removed Webcam Preview (Request: 100% Text) -->
                  </div>
                </div>
              }
              <div class="robot__helper">
                <i>{{ 'HOME.HERO.ROBOT_HELPER' | translate }}</i>
              </div>
            </div>
          </div>
        </div>

        <!-- Scroll indicator -->
        <div class="hero__scroll animate-fade-in delay-700">
          <div class="scroll-indicator">
            <div class="scroll-indicator__dot"></div>
          </div>
          <span>{{ 'HOME.HERO.SCROLL' | translate }}</span>
        </div>
      </div>

      <!-- Background decoration -->
      <div class="hero__bg-accent"></div>
    </section>
  `,
  styleUrl: './hero.component.scss',
})
export class HeroComponent {
  private http = inject(HttpClient);
  // URL relative : servie par le proxy nginx (/api -> backend) en prod,
  // et par le proxy de dev Angular (proxy.conf.json) en local.
  private readonly API_URL = '/api/chat';

  mouseX = 0;
  mouseY = 0;

  // Chat State
  isChatActive = false;
  isTyping = false;
  userInput = '';
  messages: { text: string; sender: 'user' | 'bot'; isKey?: boolean }[] = [
    { text: 'HOME.HERO.CHAT.WELCOME', sender: 'bot', isKey: true },
  ];

  @ViewChild('scrollContainer') scrollContainer!: ElementRef<HTMLDivElement>;

  @HostListener('window:mousemove', ['$event'])
  onMouseMove(event: MouseEvent) {
    // Calibrate center to the robot's right-side position (0.75)
    // Reduce intensity (1.5x instead of 2.0x) for a more forward-biased gaze
    const rawX = (event.clientX / window.innerWidth - 0.75) * 1.5;
    const rawY = (event.clientY / window.innerHeight - 0.5) * 1.5;

    this.mouseX = Math.max(-1, Math.min(1, rawX));
    this.mouseY = Math.max(-1, Math.min(1, rawY));
  }

  async toggleChat() {
    this.isChatActive = !this.isChatActive;
  }

  sendMessage() {
    if (!this.userInput.trim()) return;

    const userText = this.userInput;

    // Historique de la conversation avant le nouveau message (on exclut les
    // messages "clés" de traduction : accueil, erreurs — ce ne sont pas du contenu réel).
    const history = this.messages
      .filter((m) => !m.isKey)
      .map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

    this.messages.push({ text: userText, sender: 'user' });
    this.userInput = '';
    this.scrollToBottom();

    this.isTyping = true;

    this.http.post<{ reply: string }>(this.API_URL, { message: userText, history }).subscribe({
      next: (response) => {
        this.isTyping = false;
        this.messages.push({
          text: response.reply,
          sender: 'bot',
        });
        this.scrollToBottom();
      },
      error: (err) => {
        this.isTyping = false;
        this.messages.push({
          text: 'HOME.HERO.CHAT.ERROR',
          sender: 'bot',
          isKey: true,
        });
        console.error('Chat error:', err);
        this.scrollToBottom();
      },
    });
  }

  private scrollToBottom() {
    setTimeout(() => {
      if (this.scrollContainer) {
        this.scrollContainer.nativeElement.scrollTop =
          this.scrollContainer.nativeElement.scrollHeight;
      }
    }, 100);
  }
}
