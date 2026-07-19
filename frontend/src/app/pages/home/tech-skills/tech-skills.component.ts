import { Component, OnInit, ElementRef } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';

interface SkillBar {
  key: string;
  level: number;
  category: 'ai' | 'lang' | 'tools';
  color: string;
}

@Component({
  selector: 'app-tech-skills',
  standalone: true,
  imports: [TranslateModule],
  template: `
    <section class="section tech-skills">
      <div class="container">
        <div class="tech-grid">
          <!-- AI / ML -->
          <div class="skill-group">
            <h3 class="skill-group__title">
              <span class="skill-group__dot" style="--dot-color: #6c63ff"></span>
              {{ 'HOME.TECH_SKILLS.CATEGORIES.AI_ML' | translate }}
            </h3>
            @for (skill of aiSkills; track skill.key) {
              <div class="skill-bar-item" #skillBar>
                <div class="skill-bar-item__header">
                  <span class="skill-bar-item__name">{{
                    'HOME.TECH_SKILLS.ITEMS.' + skill.key | translate
                  }}</span>
                  <span class="skill-bar-item__level">{{ skill.level }}%</span>
                </div>
                <div class="skill-bar-item__track">
                  <div
                    class="skill-bar-item__fill"
                    [style.width]="animated ? skill.level + '%' : '0%'"
                    [style.background]="skill.color"
                  ></div>
                </div>
              </div>
            }
          </div>

          <!-- Languages -->
          <div class="skill-group">
            <h3 class="skill-group__title">
              <span class="skill-group__dot" style="--dot-color: #00d4ff"></span>
              {{ 'HOME.TECH_SKILLS.CATEGORIES.LANGUAGES' | translate }}
            </h3>
            @for (skill of langSkills; track skill.key) {
              <div class="skill-bar-item" #skillBar>
                <div class="skill-bar-item__header">
                  <span class="skill-bar-item__name">{{
                    'HOME.TECH_SKILLS.ITEMS.' + skill.key | translate
                  }}</span>
                  <span class="skill-bar-item__level">{{ skill.level }}%</span>
                </div>
                <div class="skill-bar-item__track">
                  <div
                    class="skill-bar-item__fill"
                    [style.width]="animated ? skill.level + '%' : '0%'"
                    [style.background]="skill.color"
                  ></div>
                </div>
              </div>
            }
          </div>

          <!-- Tools -->
          <div class="skill-group">
            <h3 class="skill-group__title">
              <span class="skill-group__dot" style="--dot-color: #ff63b2"></span>
              {{ 'HOME.TECH_SKILLS.CATEGORIES.TOOLS' | translate }}
            </h3>
            @for (skill of toolSkills; track skill.key) {
              <div class="skill-bar-item" #skillBar>
                <div class="skill-bar-item__header">
                  <span class="skill-bar-item__name">{{
                    'HOME.TECH_SKILLS.ITEMS.' + skill.key | translate
                  }}</span>
                  <span class="skill-bar-item__level">{{ skill.level }}%</span>
                </div>
                <div class="skill-bar-item__track">
                  <div
                    class="skill-bar-item__fill"
                    [style.width]="animated ? skill.level + '%' : '0%'"
                    [style.background]="skill.color"
                  ></div>
                </div>
              </div>
            }
          </div>
        </div>
      </div>
    </section>
  `,
  styleUrl: './tech-skills.component.scss',
})
export class TechSkillsComponent implements OnInit {
  animated = false;

  aiSkills: SkillBar[] = [
    {
      key: 'MACHINE_LEARNING',
      level: 75,
      category: 'ai',
      color: 'linear-gradient(90deg, #6c63ff, #a78bfa)',
    },
    { key: 'RAG', level: 75, category: 'ai', color: 'linear-gradient(90deg, #6c63ff, #00d4ff)' },
    {
      key: 'FINETUNING',
      level: 70,
      category: 'ai',
      color: 'linear-gradient(90deg, #d97706, #f59e0b)',
    },
    {
      key: 'AGENTIC',
      level: 65,
      category: 'ai',
      color: 'linear-gradient(90deg, #f59e0b, #ffb863)',
    },
    {
      key: 'DEEP_LEARNING',
      level: 60,
      category: 'ai',
      color: 'linear-gradient(90deg, #6c63ff, #a78bfa)',
    },
    {
      key: 'REINFORCEMENT_LEARNING',
      level: 40,
      category: 'ai',
      color: 'linear-gradient(90deg, #6c63ff, #00d4ff)',
    },
  ];

  langSkills: SkillBar[] = [
    {
      key: 'PYTHON',
      level: 80,
      category: 'lang',
      color: 'linear-gradient(90deg, #d97706, #f59e0b)',
    },
    {
      key: 'FASTAPI',
      level: 75,
      category: 'lang',
      color: 'linear-gradient(90deg, #05998b, #00d4ff)',
    },
    { key: 'SQL', level: 60, category: 'lang', color: 'linear-gradient(90deg, #78350f, #d97706)' },
    {
      key: 'KOTLIN',
      level: 50,
      category: 'lang',
      color: 'linear-gradient(90deg, #7f52ff, #a78bfa)',
    },
    { key: 'JAVA', level: 50, category: 'lang', color: 'linear-gradient(90deg, #5382a1, #00d4ff)' },
    {
      key: 'ANGULAR',
      level: 45,
      category: 'lang',
      color: 'linear-gradient(90deg, #dd0031, #f59e0b)',
    },
  ];

  toolSkills: SkillBar[] = [
    { key: 'GIT', level: 75, category: 'tools', color: 'linear-gradient(90deg, #63ffb2, #00d4ff)' },
    {
      key: 'DOCKER',
      level: 70,
      category: 'tools',
      color: 'linear-gradient(90deg, #ffb863, #ff6363)',
    },
    {
      key: 'SCIKIT',
      level: 70,
      category: 'tools',
      color: 'linear-gradient(90deg, #ff63b2, #ffa663)',
    },
    {
      key: 'MLFLOW',
      level: 60,
      category: 'tools',
      color: 'linear-gradient(90deg, #0194e2, #00d4ff)',
    },
    {
      key: 'LANGCHAIN',
      level: 60,
      category: 'tools',
      color: 'linear-gradient(90deg, #63ffb2, #00d4ff)',
    },
    {
      key: 'PYTORCH',
      level: 55,
      category: 'tools',
      color: 'linear-gradient(90deg, #ff63b2, #ff8563)',
    },
    {
      key: 'OPTUNA',
      level: 55,
      category: 'tools',
      color: 'linear-gradient(90deg, #1e3a8a, #00d4ff)',
    },
    {
      key: 'DSPY',
      level: 45,
      category: 'tools',
      color: 'linear-gradient(90deg, #5c3ee8, #a78bfa)',
    },
    {
      key: 'VLLM',
      level: 45,
      category: 'tools',
      color: 'linear-gradient(90deg, #ff63b2, #ffa663)',
    },
  ];

  constructor(private el: ElementRef) {}

  ngOnInit(): void {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !this.animated) {
          this.animated = true;
        }
      },
      { threshold: 0.2 },
    );
    observer.observe(this.el.nativeElement);
  }
}
