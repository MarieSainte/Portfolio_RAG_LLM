import { AfterViewInit, Component, ElementRef, HostListener, ViewChild } from '@angular/core';
import { TranslateModule } from '@ngx-translate/core';
import { Domain, DOMAIN_COLORS, PROJECT_NODES, ProjectNodeData } from './mind-map.data';

type ChildType = 'MISSIONS' | 'STACK' | 'SOFT' | 'FACT';

interface ChildNode {
  type: ChildType;
  x: number;
  y: number;
  link: string;
}

interface LaidNode {
  data: ProjectNodeData;
  x: number;
  y: number;
  link: string;
  children: ChildNode[];
  // Link pills anchored on the branch, between the center and the node
  linkX: number;
  linkY: number;
}

const CANVAS = 2600;
const CENTER = CANVAS / 2;
// Elliptical layout: wide on the sides, flat on top/bottom (screens are wide)
const RX_INNER = 560;
const RY_INNER = 330;
const RX_OUTER = 790;
const RY_OUTER = 465;
const CHILD_DIST = 340;

@Component({
  selector: 'app-mind-map',
  standalone: true,
  imports: [TranslateModule],
  template: `
    <div class="page-enter mind-map-page">
      <div
        class="mm-viewport"
        #viewport
        (wheel)="onWheel($event)"
        (pointerdown)="onPointerDown($event)"
        (pointermove)="onPointerMove($event)"
        (pointerup)="onPointerUp($event)"
        (pointercancel)="onPointerUp($event)"
      >
        <div class="mm-bg" aria-hidden="true"></div>
        <div
          class="mm-canvas"
          [class.mm-canvas--animate]="animating"
          [class.mm-canvas--dimmed]="expandedId !== null"
          [style.transform]="canvasTransform"
        >
          <div class="mm-halo" aria-hidden="true"></div>
          <svg
            class="mm-links"
            [attr.width]="canvasSize"
            [attr.height]="canvasSize"
            [attr.viewBox]="'0 0 ' + canvasSize + ' ' + canvasSize"
            aria-hidden="true"
          >
            @for (n of nodes; track n.data.id) {
              <path
                [attr.d]="n.link"
                class="mm-link"
                [class.mm-link--active]="expandedId === n.data.id || hoverId === n.data.id"
                [attr.stroke]="domainColors[n.data.domain]"
              />
            }
            @if (expandedNode; as en) {
              @for (c of en.children; track c.type) {
                <path
                  [attr.d]="c.link"
                  class="mm-link mm-link--child"
                  [attr.stroke]="domainColors[en.data.domain]"
                />
              }
            }
          </svg>

          <div
            class="mm-center"
            [style.left.px]="center"
            [style.top.px]="center"
            (pointerdown)="$event.stopPropagation()"
            (click)="collapse()"
          >
            <span class="mm-center__name">{{ 'MIND_MAP.ROOT_NAME' | translate }}</span>
            <span class="mm-center__role">{{ 'MIND_MAP.ROOT_ROLE' | translate }}</span>
          </div>

          @for (n of nodes; track n.data.id; let i = $index) {
            <button
              type="button"
              class="mm-node"
              [class.mm-node--open]="expandedId === n.data.id"
              [style.left.px]="n.x"
              [style.top.px]="n.y"
              [style.--node-color]="domainColors[n.data.domain]"
              [style.--i]="i"
              (pointerdown)="$event.stopPropagation()"
              (click)="toggle(n)"
              (mouseenter)="hoverId = n.data.id"
              (mouseleave)="hoverId = null"
            >
              <span class="mm-node__icon">{{ n.data.icon }}</span>
              <span class="mm-node__label">{{
                'MIND_MAP.' + n.data.id + '.SHORT' | translate
              }}</span>
            </button>
          }

          @if (expandedNode; as en) {
            @if (en.data.links?.length) {
              <div
                class="mm-linkbar"
                [style.left.px]="en.linkX"
                [style.top.px]="en.linkY"
                [style.--node-color]="domainColors[en.data.domain]"
                (pointerdown)="$event.stopPropagation()"
              >
                @for (l of en.data.links; track l.url) {
                  <a class="mm-pill-link" [href]="l.url" target="_blank" rel="noopener">
                    @if (l.label === 'GitHub') {
                      <svg
                        width="12"
                        height="12"
                        viewBox="0 0 24 24"
                        fill="currentColor"
                        aria-hidden="true"
                      >
                        <path
                          d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.166 6.839 9.489.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.341-3.369-1.341-.454-1.155-1.11-1.462-1.11-1.462-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0 1 12 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.202 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.138 20.163 22 16.418 22 12c0-5.523-4.477-10-10-10z"
                        />
                      </svg>
                    } @else {
                      <svg
                        width="11"
                        height="11"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2.2"
                        aria-hidden="true"
                      >
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                        <polyline points="15 3 21 3 21 9" />
                        <line x1="10" y1="14" x2="21" y2="3" />
                      </svg>
                    }
                    {{ l.label }}
                  </a>
                }
              </div>
            }
            @for (c of en.children; track c.type) {
              <div
                class="mm-child"
                [class.mm-child--fact]="c.type === 'FACT'"
                [style.left.px]="c.x"
                [style.top.px]="c.y"
                [style.--node-color]="domainColors[en.data.domain]"
                (pointerdown)="$event.stopPropagation()"
              >
                <span class="mm-child__label">{{ 'MIND_MAP.LABEL.' + c.type | translate }}</span>
                @if (c.type === 'STACK') {
                  <div class="mm-child__tags">
                    @for (t of en.data.stack; track t) {
                      <span class="mm-tag">{{ t }}</span>
                    }
                  </div>
                } @else {
                  <p>{{ 'MIND_MAP.' + en.data.id + '.' + c.type | translate }}</p>
                }
              </div>
            }
          }
        </div>

        <div class="mm-controls" (pointerdown)="$event.stopPropagation()">
          <button
            type="button"
            (click)="zoomBy(1.25)"
            [attr.aria-label]="'MIND_MAP.ZOOM_IN' | translate"
          >
            +
          </button>
          <button
            type="button"
            (click)="zoomBy(0.8)"
            [attr.aria-label]="'MIND_MAP.ZOOM_OUT' | translate"
          >
            −
          </button>
          <button type="button" (click)="fit()" [attr.aria-label]="'MIND_MAP.RESET' | translate">
            ⌂
          </button>
        </div>

        <p class="mm-hint">{{ 'MIND_MAP.HINT' | translate }}</p>
      </div>
    </div>
  `,
  styleUrl: './mind-map.component.scss',
})
export class MindMapComponent implements AfterViewInit {
  @ViewChild('viewport') viewportRef!: ElementRef<HTMLDivElement>;

  readonly canvasSize = CANVAS;
  readonly center = CENTER;
  readonly domainColors: Record<Domain, string> = DOMAIN_COLORS;

  nodes: LaidNode[] = [];
  expandedId: string | null = null;
  hoverId: string | null = null;

  scale = 0.35;
  tx = 0;
  ty = 0;
  animating = false;

  private savedView: { tx: number; ty: number; scale: number } | null = null;
  private dragging = false;
  private dragDist = 0;
  private lastX = 0;
  private lastY = 0;
  private userMoved = false;
  private animTimer: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    this.nodes = PROJECT_NODES.map((data, i) => this.layoutNode(data, i));
  }

  get canvasTransform(): string {
    return `translate(${this.tx}px, ${this.ty}px) scale(${this.scale})`;
  }

  get expandedNode(): LaidNode | null {
    return this.nodes.find((n) => n.data.id === this.expandedId) ?? null;
  }

  ngAfterViewInit(): void {
    requestAnimationFrame(() => this.fit());
  }

  // ---------- Layout ----------

  private layoutNode(data: ProjectNodeData, i: number): LaidNode {
    const angle = (-90 + i * (360 / PROJECT_NODES.length)) * (Math.PI / 180);
    const rx = i % 2 === 0 ? RX_INNER : RX_OUTER;
    const ry = i % 2 === 0 ? RY_INNER : RY_OUTER;
    const x = CENTER + rx * Math.cos(angle);
    const y = CENTER + ry * Math.sin(angle);
    // Actual direction from the center to the node (differs from the
    // parametric angle on an ellipse) — used for fans, links and anchors
    const dir = Math.atan2(y - CENTER, x - CENTER);

    // Curved link from the central node, alternating bend for an organic look
    const mx = (CENTER + x) / 2;
    const my = (CENTER + y) / 2;
    const bend = (i % 2 === 0 ? 1 : -1) * 46;
    const cx = mx + bend * Math.cos(dir + Math.PI / 2);
    const cy = my + bend * Math.sin(dir + Math.PI / 2);
    const link = `M ${CENTER} ${CENTER} Q ${cx} ${cy} ${x} ${y}`;

    const types: ChildType[] = data.hasFact
      ? ['MISSIONS', 'STACK', 'SOFT', 'FACT']
      : ['MISSIONS', 'STACK', 'SOFT'];
    const offsets = data.hasFact ? [-57, -19, 19, 57] : [-38, 0, 38];

    const children: ChildNode[] = types.map((type, j) => {
      const a = dir + offsets[j] * (Math.PI / 180);
      const chx = x + CHILD_DIST * Math.cos(a);
      const chy = y + CHILD_DIST * Math.sin(a);
      return { type, x: chx, y: chy, link: `M ${x} ${y} L ${chx} ${chy}` };
    });

    // Barre de lien GitHub : toujours DIRECTEMENT au-dessus du nœud, quelle que
    // soit sa position sur l'ellipse (centrée horizontalement).
    const linkX = x;
    const linkY = y - 64;

    return { data, x, y, link, children, linkX, linkY };
  }

  // ---------- Interactions ----------

  toggle(node: LaidNode): void {
    if (this.expandedId === node.data.id) {
      this.collapse();
      return;
    }
    // Remember the overview so closing the project restores it
    if (this.expandedId === null) {
      this.savedView = { tx: this.tx, ty: this.ty, scale: this.scale };
    }
    this.expandedId = node.data.id;

    const vp = this.viewportRef.nativeElement.getBoundingClientRect();
    const targetScale = Math.max(this.scale, 0.85);
    // Focus point: slightly beyond the project node, toward its children fan
    const angle = Math.atan2(node.y - CENTER, node.x - CENTER);
    const fx = node.x + 170 * Math.cos(angle);
    const fy = node.y + 170 * Math.sin(angle);

    this.scale = targetScale;
    this.tx = vp.width / 2 - fx * targetScale;
    this.ty = vp.height / 2 - fy * targetScale;
    this.startAnimation();
  }

  collapse(): void {
    if (this.expandedId === null) return;
    this.expandedId = null;
    if (this.savedView) {
      this.tx = this.savedView.tx;
      this.ty = this.savedView.ty;
      this.scale = this.savedView.scale;
      this.savedView = null;
      this.startAnimation();
    }
  }

  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.collapse();
  }

  @HostListener('window:resize')
  onResize(): void {
    if (!this.userMoved) this.fit();
  }

  fit(): void {
    const vp = this.viewportRef?.nativeElement;
    if (!vp) return;
    const { width, height } = vp.getBoundingClientRect();
    // Frame the elliptical project ring so the nodes stay readable
    this.scale = Math.min(width / 1820, height / 1060, 1);
    this.tx = width / 2 - CENTER * this.scale;
    this.ty = height / 2 - CENTER * this.scale;
    this.userMoved = false;
    this.startAnimation();
  }

  zoomBy(factor: number): void {
    const vp = this.viewportRef.nativeElement.getBoundingClientRect();
    this.applyZoom(factor, vp.width / 2, vp.height / 2);
  }

  onWheel(event: WheelEvent): void {
    event.preventDefault();
    this.stopAnimation();
    const rect = this.viewportRef.nativeElement.getBoundingClientRect();
    const factor = event.deltaY < 0 ? 1.15 : 1 / 1.15;
    this.applyZoom(factor, event.clientX - rect.left, event.clientY - rect.top);
    this.userMoved = true;
  }

  private applyZoom(factor: number, px: number, py: number): void {
    const next = Math.min(2.5, Math.max(0.18, this.scale * factor));
    this.tx = px - ((px - this.tx) * next) / this.scale;
    this.ty = py - ((py - this.ty) * next) / this.scale;
    this.scale = next;
  }

  onPointerDown(event: PointerEvent): void {
    this.stopAnimation();
    this.dragging = true;
    this.dragDist = 0;
    this.lastX = event.clientX;
    this.lastY = event.clientY;
    this.viewportRef.nativeElement.setPointerCapture(event.pointerId);
  }

  onPointerMove(event: PointerEvent): void {
    if (!this.dragging) return;
    const dx = event.clientX - this.lastX;
    const dy = event.clientY - this.lastY;
    this.dragDist += Math.abs(dx) + Math.abs(dy);
    this.tx += dx;
    this.ty += dy;
    this.lastX = event.clientX;
    this.lastY = event.clientY;
    this.userMoved = true;
  }

  onPointerUp(event: PointerEvent): void {
    if (!this.dragging) return;
    this.dragging = false;
    this.viewportRef.nativeElement.releasePointerCapture(event.pointerId);
    // A simple click on the background (no real drag) closes the open project
    if (this.dragDist < 5) this.collapse();
  }

  private startAnimation(): void {
    this.animating = true;
    if (this.animTimer) clearTimeout(this.animTimer);
    this.animTimer = setTimeout(() => (this.animating = false), 550);
  }

  private stopAnimation(): void {
    this.animating = false;
    if (this.animTimer) clearTimeout(this.animTimer);
  }
}
