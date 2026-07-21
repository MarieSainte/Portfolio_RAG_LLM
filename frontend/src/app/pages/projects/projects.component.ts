import { Component } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { CommonModule } from '@angular/common';

type FilterType = 'all' | 'student' | 'personal';

interface Project {
  id: number;
  titleKey: string;
  descKey: string;
  longDescKey?: string;
  tags: string[];
  type: 'student' | 'personal';
  github?: string;
  demo?: string;
  pptUrl?: string;
  videoUrl?: string;
  icon: string;
  color: string;
}

@Component({
  selector: 'app-projects',
  standalone: true,
  imports: [TranslateModule, CommonModule],
  template: `
    <div class="page-enter projects-page">
      <div class="container">
        <!-- Filters -->
        <div class="filters" style="padding-top: 100px">
          <button
            class="filter-btn"
            [class.filter-btn--active]="activeFilter === 'all'"
            (click)="setFilter('all')"
          >
            {{ 'PROJECTS.FILTER.ALL' | translate }}
            <span class="filter-btn__count">{{ projects.length }}</span>
          </button>
          <button
            class="filter-btn"
            [class.filter-btn--active]="activeFilter === 'student'"
            (click)="setFilter('student')"
          >
            {{ 'PROJECTS.FILTER.STUDENT' | translate }}
            <span class="filter-btn__count">{{ studentCount }}</span>
          </button>
          <button
            class="filter-btn"
            [class.filter-btn--active]="activeFilter === 'personal'"
            (click)="setFilter('personal')"
          >
            {{ 'PROJECTS.FILTER.PERSONAL' | translate }}
            <span class="filter-btn__count">{{ personalCount }}</span>
          </button>
        </div>

        <!-- Projects Grid -->
        <div class="projects-grid">
          @for (project of filteredProjects; track project.id) {
            <div class="project-card" [style.--card-accent]="project.color">
              <div class="project-card__top">
                <div class="project-card__icon">{{ project.icon }}</div>
                <span
                  class="badge"
                  [class.badge--accent]="project.type === 'student'"
                  [class.badge--cyan]="project.type === 'personal'"
                >
                  {{
                    (project.type === 'student'
                      ? 'PROJECTS.CARD.STUDENT_LABEL'
                      : 'PROJECTS.CARD.PERSONAL_LABEL'
                    ) | translate
                  }}
                </span>
              </div>

              <h3 class="project-card__title">{{ project.titleKey | translate }}</h3>
              <p class="project-card__desc">{{ project.descKey | translate }}</p>

              <div class="project-card__tags">
                @for (tag of project.tags; track tag) {
                  <span class="tag">{{ tag }}</span>
                }
              </div>

              <div class="project-card__actions">
                @if (project.github) {
                  <a
                    [href]="project.github"
                    target="_blank"
                    rel="noopener"
                    class="btn btn--ghost btn--sm"
                    (click)="$event.stopPropagation()"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path
                        d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.341-3.369-1.341-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"
                      />
                    </svg>
                    {{ 'PROJECTS.CARD.CODE' | translate }}
                  </a>
                }
                <button class="btn btn--outline btn--sm" (click)="openProject(project)">
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                  {{ 'PROJECTS.CARD.VIEW' | translate }}
                </button>
              </div>

              <div class="project-card__glow"></div>
            </div>
          }
        </div>

        @if (filteredProjects.length === 0) {
          <div class="empty-state">
            <p>{{ 'PROJECTS.EMPTY' | translate }}</p>
          </div>
        }
      </div>
    </div>

    <!-- Modal Details -->
    @if (selectedProject) {
      <div class="modal-overlay" (click)="closeModal()" [class.modal-active]="selectedProject">
        <div class="modal-content" (click)="$event.stopPropagation()">
          <button class="modal-close" (click)="closeModal()">
            <svg
              viewBox="0 0 24 24"
              width="24"
              height="24"
              stroke="currentColor"
              stroke-width="2"
              fill="none"
            >
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>

          <div class="modal-header">
            <div class="modal-icon">{{ selectedProject.icon }}</div>
            <div class="modal-title-group">
              <span
                class="badge badge--sm"
                [class.badge--accent]="selectedProject.type === 'student'"
                [class.badge--cyan]="selectedProject.type === 'personal'"
              >
                {{
                  (selectedProject.type === 'student'
                    ? 'PROJECTS.CARD.STUDENT_LABEL'
                    : 'PROJECTS.CARD.PERSONAL_LABEL'
                  ) | translate
                }}
              </span>
              <h2 class="modal-title">{{ selectedProject.titleKey | translate }}</h2>
            </div>
          </div>

          <div class="modal-body">
            <div class="modal-info">
              <h3 class="modal-subtitle">{{ 'PROJECTS.MODAL.DESCRIPTION' | translate }}</h3>
              <p class="modal-desc">{{ selectedProject.descKey | translate }}</p>

              <div class="modal-tags">
                @for (tag of selectedProject.tags; track tag) {
                  <span class="tag">{{ tag }}</span>
                }
              </div>

              <div class="modal-links">
                @if (selectedProject.github) {
                  <a [href]="selectedProject.github" target="_blank" class="btn btn--ghost"
                    >GitHub</a
                  >
                }
                @if (selectedProject.pptUrl) {
                  <a [href]="selectedProject.pptUrl" target="_blank" class="btn btn--outline"
                    >PowerPoint</a
                  >
                }
              </div>
            </div>

            <!-- Media Section (Placeholder for future video/ppt embed) -->
            @if (selectedProject.videoUrl || selectedProject.pptUrl) {
              <div class="modal-media">
                <div class="video-container">
                  <div class="media-placeholder">
                    <svg viewBox="0 0 24 24" width="48" height="48" fill="rgba(255,255,255,0.2)">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                    <span>{{ 'PROJECTS.MODAL.MEDIA_SOON' | translate }}</span>
                  </div>
                </div>
              </div>
            }
          </div>
        </div>
      </div>
    }
  `,
  styleUrl: './projects.component.scss',
})
export class ProjectsComponent {
  activeFilter: FilterType = 'all';
  selectedProject: Project | null = null;

  projects: Project[] = [
    {
      id: 5,
      titleKey: 'PROJECTS.SENTINEL.TITLE',
      descKey: 'PROJECTS.SENTINEL.DESC',
      tags: [
        'En cours',
        'Qwen3 · SFT',
        'LangGraph',
        'PostgreSQL',
        'Neo4j',
        'Milvus',
        'FastAPI',
        'React',
        'RunPod',
      ],
      type: 'personal',
      icon: '🕵️',
      color: '#06b6d4',
    },
    {
      id: 1,
      titleKey: 'PROJECTS.STUDENT_1.TITLE',
      descKey: 'PROJECTS.STUDENT_1.DESC',
      tags: ['Qwen3-1.7B', 'SFT/DPO', 'vLLM', 'DSPy', 'Docker', 'CI/CD', 'OVH'],
      type: 'student',
      github: 'https://github.com/MarieSainte/triage-medical-chatbot',
      icon: '🩺',
      color: '#ff4d4d',
    },
    {
      id: 4,
      titleKey: 'PROJECTS.NEUROVA.TITLE',
      descKey: 'PROJECTS.NEUROVA.DESC',
      tags: ['Flutter', 'Rust · Axum', 'WebSocket', 'PostgreSQL', 'Redis', 'AdMob'],
      type: 'personal',
      icon: '🧠',
      color: '#c9a227',
    },
    {
      id: 2,
      titleKey: 'PROJECTS.STUDENT_2.TITLE',
      descKey: 'PROJECTS.STUDENT_2.DESC',
      tags: ['LangGraph', 'FastAPI', 'Milvus', 'Stockfish', 'MongoDB', 'Angular'],
      type: 'student',
      github: 'https://github.com/MarieSainte/ffe-ai',
      icon: '♟️',
      color: '#e0e0e0',
    },
    {
      id: 3,
      titleKey: 'PROJECTS.PORTFOLIO.TITLE',
      descKey: 'PROJECTS.PORTFOLIO.DESC',
      tags: ['Angular', 'FastAPI', 'RAG', 'ChromaDB', 'SQLite', 'Mistral AI', 'Docker', 'OVH'],
      type: 'personal',
      github: 'https://github.com/MarieSainte/Portfolio_RAG_LLM',
      icon: '🌐',
      color: '#f59e0b',
    },
  ];

  get filteredProjects(): Project[] {
    if (this.activeFilter === 'all') return this.projects;
    return this.projects.filter((p) => p.type === this.activeFilter);
  }

  get studentCount(): number {
    return this.projects.filter((p) => p.type === 'student').length;
  }

  get personalCount(): number {
    return this.projects.filter((p) => p.type === 'personal').length;
  }

  setFilter(filter: FilterType): void {
    this.activeFilter = filter;
  }

  openProject(project: Project): void {
    this.selectedProject = project;
    document.body.style.overflow = 'hidden';
  }

  closeModal(): void {
    this.selectedProject = null;
    document.body.style.overflow = '';
  }
}
