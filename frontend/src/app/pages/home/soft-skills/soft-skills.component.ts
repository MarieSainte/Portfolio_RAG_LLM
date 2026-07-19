import { Component } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

interface SoftSkill {
  key: string;
  icon: string;
  color: string;
}

@Component({
  selector: 'app-soft-skills',
  standalone: true,
  imports: [TranslateModule],
  template: `
    <section class="section soft-skills">
      <div class="container">
        <div class="skills-grid">
          @for (skill of skills; track skill.key) {
            <div class="skill-card" [style.--card-color]="skill.color">
              <div class="skill-card__icon">{{ skill.icon }}</div>
              <h3 class="skill-card__title">
                {{ 'HOME.SKILLS.ITEMS.' + skill.key + '.TITLE' | translate }}
              </h3>
              <p class="skill-card__desc">
                {{ 'HOME.SKILLS.ITEMS.' + skill.key + '.DESC' | translate }}
              </p>
              <div class="skill-card__accent"></div>
            </div>
          }
        </div>
      </div>
    </section>
  `,
  styleUrl: './soft-skills.component.scss',
})
export class SoftSkillsComponent {
  skills: SoftSkill[] = [
    { key: 'ANALYSIS', icon: '🔎', color: '#6c63ff' },
    { key: 'PROBLEM_SOLVING', icon: '🧩', color: '#00d4ff' },
    { key: 'CURIOSITY', icon: '🧐', color: '#ff63b2' },
    { key: 'CREATIVITY', icon: '✨', color: '#63ffb2' },
    { key: 'BUSINESS', icon: '💼', color: '#ffb863' },
    { key: 'LEARNING', icon: '🚀', color: '#a78bfa' },
  ];
}
