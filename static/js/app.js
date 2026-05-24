/**
 * Inicialización Alpine.js + helpers globales para la app educativa.
 */

// Store global de Alpine para el theme + modal de imagen
document.addEventListener('alpine:init', () => {
  // Modal global para expandir imágenes a pantalla completa
  Alpine.store('imageModal', {
    open: false,
    src: '',
    alt: '',
    show(src, alt) {
      this.src = src;
      this.alt = alt || '';
      this.open = true;
      document.body.style.overflow = 'hidden';
    },
    close() {
      this.open = false;
      document.body.style.overflow = '';
    },
  });

  Alpine.store('theme', {
    init() {
      // Detectar preferencia: localStorage > system preference > light
      const saved = localStorage.getItem('theme');
      if (saved) {
        this.current = saved;
      } else {
        this.current = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      }
      this.apply();

      // Escuchar cambios del sistema
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
          this.current = e.matches ? 'dark' : 'light';
          this.apply();
        }
      });
    },
    current: 'light',
    toggle() {
      this.current = this.current === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', this.current);
      this.apply();
    },
    apply() {
      if (this.current === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    },
  });
});

// Modal de imagen GARANTIZADO crea overlay DOM puro, no depende de Alpine.
// Funciona incluso con HTMX swaps porque es JS vanilla.
window.openImageModal = function(src, alt) {
  console.log('[openImageModal] abriendo:', src ? src.substring(0,50) : 'sin src');

  // Eliminar overlay previo si existe
  const existing = document.getElementById('__img_modal_overlay');
  if (existing) existing.remove();

  // Crear overlay
  const overlay = document.createElement('div');
  overlay.id = '__img_modal_overlay';
  overlay.style.cssText = [
    'position:fixed',
    'inset:0',
    'z-index:999999',
    'background:rgba(0,0,0,0.93)',
    'display:flex',
    'align-items:center',
    'justify-content:center',
    'padding:2rem',
    'cursor:zoom-out',
    'animation:fadeInModal 0.2s ease-out'
  ].join(';');

  // Imagen ampliada fondo BLANCO para que las gráficas matplotlib con fondo
  // transparente se vean correctamente sobre el overlay oscuro.
  const img = document.createElement('img');
  img.src = src;
  img.alt = alt || '';
  img.style.cssText = 'max-width:95vw; max-height:90vh; object-fit:contain; border-radius:10px; box-shadow:0 30px 80px rgba(0,0,0,0.6); cursor:zoom-out; background-color:#ffffff; padding:16px;';

  // Botón cerrar
  const closeBtn = document.createElement('button');
  closeBtn.type = 'button';
  closeBtn.setAttribute('aria-label', 'Cerrar');
  closeBtn.style.cssText = 'position:absolute; top:20px; right:20px; width:44px; height:44px; border-radius:8px; background:rgba(255,255,255,0.95); border:none; cursor:pointer; display:flex; align-items:center; justify-content:center; box-shadow:0 4px 12px rgba(0,0,0,0.3);';
  closeBtn.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#111" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';

  // Hint inferior
  const hint = document.createElement('div');
  hint.style.cssText = 'position:absolute; bottom:24px; left:50%; transform:translateX(-50%); color:rgba(255,255,255,0.85); font-size:12px; padding:6px 14px; background:rgba(0,0,0,0.5); border-radius:999px; border:1px solid rgba(255,255,255,0.15);';
  hint.textContent = 'Click fuera o ESC para cerrar';

  overlay.appendChild(img);
  overlay.appendChild(closeBtn);
  overlay.appendChild(hint);

  // Inyectar keyframes de animación una vez
  if (!document.getElementById('__img_modal_kf')) {
    const style = document.createElement('style');
    style.id = '__img_modal_kf';
    style.textContent = '@keyframes fadeInModal{from{opacity:0}to{opacity:1}}';
    document.head.appendChild(style);
  }

  // Cerrar al click overlay / botón
  const cerrar = () => {
    overlay.remove();
    document.removeEventListener('keydown', escHandler);
    document.body.style.overflow = '';
  };
  overlay.addEventListener('click', cerrar);
  closeBtn.addEventListener('click', (e) => { e.stopPropagation(); cerrar(); });
  img.addEventListener('click', (e) => e.stopPropagation()); // no cerrar al click en la imagen
  const escHandler = (e) => { if (e.key === 'Escape') cerrar(); };
  document.addEventListener('keydown', escHandler);

  // Bloquear scroll del body
  document.body.style.overflow = 'hidden';

  // Insertar
  document.body.appendChild(overlay);
};

// NOTA: View Transitions API removida intencionalmente.
// Interfería con el procesamiento de OOB swaps de HTMX (hx-swap-oob),
// rompiendo la sincronización del hero/parámetros con el formulario.
// Los swaps de HTMX usan la animación CSS animate-fade-in del propio contenido.

// GUARDIA GLOBAL: prevenir submit nativo en CUALQUIER formulario HTMX.
// Si HTMX no llega a interceptar (porque aún no cargó, o por race conditions),
// el browser haría una navegación nativa al endpoint del form (hx-post),
// mostrando la respuesta cruda como página → "envía a otra vista" bug.
// Esto bloquea ese comportamiento incondicionalmente para forms con hx-post.
document.addEventListener('submit', function(e) {
  var form = e.target;
  if (form && form.tagName === 'FORM' && form.hasAttribute('hx-post')) {
    e.preventDefault();
    // Si HTMX está cargado, dispararlo manualmente; si no, no hacer nada (silencioso)
    if (window.htmx) {
      try { window.htmx.trigger(form, 'submit'); } catch (err) { console.warn('htmx.trigger error:', err); }
    }
  }
}, true); // captura en fase de captura, antes que cualquier otro handler

// GUARDIA ADICIONAL: prevenir Enter en inputs numéricos/text que dispara submit por defecto
document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && e.target && e.target.tagName === 'INPUT') {
    var type = (e.target.type || '').toLowerCase();
    if (type === 'number' || type === 'text' || type === '') {
      var form = e.target.closest('form');
      if (form && form.hasAttribute('hx-post')) {
        e.preventDefault();
        // Disparar HTMX manualmente para que recalcule
        if (window.htmx) {
          try { window.htmx.trigger(form, 'submit'); } catch (err) {}
        }
      }
    }
  }
}, true);

// GLOSARIO TÉCNICO: definiciones de términos que aparecen en tooltips/textos.
// El sistema busca estos términos en cualquier nodo de texto y los hace clickeables.
window.TECHNICAL_GLOSSARY = {
  "Hefner": "<strong>Otto Hefner-Alteneck</strong> (1845-1904), ingeniero eléctrico alemán de Siemens & Halske. Su fórmula empírica para tensión de línea data del siglo XIX y se popularizó en Europa central. Tiende a sobreestimar para potencias grandes es una cota SUPERIOR conservadora.",
  "Still": "<strong>Alfred Still</strong>, ingeniero eléctrico estadounidense, autor del clásico 'Overhead Electric Power Transmission' (1913). Su fórmula combina factores de longitud (en millas, por eso aparece /1.609) y potencia. Ampliamente usada en Latinoamérica por su precisión balanceada.",
  "Peek": "<strong>Frank W. Peek Jr.</strong> (1881-1933), ingeniero de General Electric. Desarrolló la fórmula empírica clásica para el gradiente crítico de ionización del aire (Ec), que predice cuándo aparece el efecto Corona. Publicada en 'Dielectric Phenomena in High Voltage Engineering' (1915).",
  "ABCD": "<strong>Parámetros ABCD</strong> son los 4 coeficientes complejos del modelo de cuadripolo que representa una línea de transmisión larga. A=D=cosh(γL), B=Zc·sinh(γL), C=sinh(γL)/Zc. Permiten calcular la tensión y corriente en un extremo conociendo el otro: VG=A·VR+B·IR.",
  "Ferranti": "<strong>Efecto Ferranti</strong>: en líneas largas con poca carga (o vacío), la tensión del extremo receptor (VR) puede ser MAYOR que la del generador (VG) debido a la capacitancia distribuida. Descubierto por Sebastian Ferranti en 1890. Se controla con reactores en derivación.",
  "Corona": "<strong>Efecto Corona</strong>: ionización del aire alrededor del conductor cuando el campo eléctrico supera el gradiente crítico (Ec 30 kV/cm a nivel del mar). Produce pérdidas, ruido audible, interferencia radio y ozono. Se evita usando haz de subconductores o conductor de mayor diámetro.",
  "ACSR": "<strong>Aluminum Conductor Steel Reinforced</strong>. Cable con hilos de aluminio dispuestos en capas alrededor de un alma de acero galvanizado. Es el conductor más común en transmisión. Ejemplos: Drake, Bluejay, Bittern. Combina buena conductividad (aluminio) con resistencia mecánica (acero).",
  "AAAC": "<strong>All Aluminum Alloy Conductor</strong>. Cable hecho 100% con aleación de aluminio. Más liviano que ACSR, mejor resistencia a la corrosión. Ideal para zonas costeras o ambientes salinos donde el acero se oxida.",
  "ACAR": "<strong>Aluminum Conductor Alloy Reinforced</strong>. Alma de aleación de aluminio + capas de aluminio puro. Excelente compromiso entre resistencia mecánica y conductividad. Muy usado en zonas con contaminación industrial.",
  "ACSS": "<strong>Aluminum Conductor Steel Supported</strong>. Variante del ACSR donde el aluminio está recocido (annealed) → el ACERO soporta toda la carga mecánica y el aluminio solo conduce. Permite operar hasta 200°C sin degradación. Usado para REPOTENCIAR líneas existentes sin cambiar torres.",
  "EHS": "<strong>Extra High Strength steel</strong>. Acero galvanizado de muy alta resistencia mecánica (~1116 MPa, vs 299 MPa del ACSR). Estándar para cables de guarda. Soporta cargas de viento extremo en la cúspide de la torre.",
  "OPGW": "<strong>Optical Ground Wire</strong> (cable de guarda óptico). Cable de guarda que incluye fibras ópticas en su interior. Combina protección contra rayos + telecomunicaciones (SCADA, voz, datos). Estándar en líneas modernas de 500 kV.",
  "BIL": "<strong>Basic Insulation Level</strong>: máxima sobretensión por impulso de rayo que debe soportar el aislamiento sin flameo. Para 500 kV el BIL es 1550 kV (IEC 60071). Determina el número mínimo de discos en la cadena de aisladores.",
  "RETIE": "<strong>Reglamento Técnico de Instalaciones Eléctricas</strong> (Colombia). Norma obligatoria emitida por el Ministerio de Minas y Energía que regula todos los aspectos técnicos y de seguridad de instalaciones eléctricas, incluyendo líneas de transmisión.",
  "IEC": "<strong>International Electrotechnical Commission</strong>. Organización internacional con sede en Ginebra que publica las normas técnicas globales de electricidad y electrónica. Las normas IEC 60071 (coordinación de aislamiento), 60815 (contaminación), 60826 (diseño mecánico) son referencia obligatoria.",
  "NTC": "<strong>Norma Técnica Colombiana</strong>. Estándar emitido por ICONTEC (Instituto Colombiano de Normas Técnicas). Suele ser adopción de normas IEC/ASTM con ajustes locales. NTC 1340 normaliza tensiones de transmisión en Colombia.",
  "UPME": "<strong>Unidad de Planeación Minero-Energética</strong> (Colombia). Entidad adscrita al Ministerio de Minas. Define el Plan de Expansión de Referencia: qué líneas/subestaciones deben construirse y a qué nivel de tensión.",
  "CREG": "<strong>Comisión de Regulación de Energía y Gas</strong> (Colombia). Regula tarifas, calidad del servicio y reglas del mercado eléctrico. La Resolución CREG 097/2008 regula la transmisión nacional (STN).",
  "GMD": "<strong>Geometric Mean Distance</strong> (Distancia Media Geométrica). Es la media geométrica de las distancias entre las 3 fases: GMD = ∛(D12·D23·D13). Se usa porque las fases NO están a igual distancia, y necesitamos una distancia EQUIVALENTE para inductancia y capacitancia.",
  "GMR": "<strong>Geometric Mean Radius</strong> (Radio Medio Geométrico). Radio equivalente del conductor (o del haz de subconductores) considerando su distribución espacial. Para un conductor sólido: GMR = r·e^(-1/4). Para cables trenzados típicamente GMR 0.78·r.",
  "SIL": "<strong>Surge Impedance Loading</strong> (potencia natural). Potencia para la cual la línea opera con factor de potencia unitario y NO hay efecto Ferranti. SIL = V²/Zc. Para 500 kV con Zc400 Ω: SIL 625 MW. Punto óptimo de operación.",
  "HVDC": "<strong>High Voltage Direct Current</strong>. Transmisión en corriente continua de alta tensión. Más eficiente que HVAC para distancias > 600 km o cuando se interconectan sistemas asíncronos. Ejemplos: línea Itaipú-Brasil ±600 kV.",
  "EDS": "<strong>Every Day Stress</strong> (esfuerzo diario). Condición climática promedio de operación normal (sin viento, temperatura habitual). RETIE exige FS=5 en EDS para evitar fatiga del conductor por vibración eólica.",
  "Ec": "<strong>Gradiente crítico de Peek</strong> (kV/cm): campo eléctrico mínimo que ioniza el aire en la superficie del conductor. A nivel del mar: ~30 kV/cm. Si el gradiente real Esup supera Ec → aparece efecto Corona permanente.",
  "Esup": "<strong>Gradiente superficial del haz</strong> (kV/cm): campo eléctrico en la superficie de los subconductores cuando la línea opera a tensión nominal. Depende del número de subconductores, su radio, la separación db y la GMD.",
  "Cs": "<strong>Coeficiente de seguridad Corona</strong> = Ec/Esup. Debe ser > 1 para que NO haya efecto Corona. Idealmente Cs ≥ 1.1-1.2 para dar margen ante lluvia (que reduce Ec ~15%)."
};

// Envuelve términos del glosario en spans clickeables. Procesa solo NODOS DE TEXTO
// para no romper HTML existente. Cada término solo se envuelve la PRIMERA vez por elemento.
window.aplicarGlosario = function(rootEl) {
  if (!rootEl || !window.TECHNICAL_GLOSSARY) return;
  var terms = Object.keys(window.TECHNICAL_GLOSSARY).sort(function(a,b){return b.length-a.length;});
  // Regex que coincide con cualquier término del glosario como palabra completa
  var pattern = new RegExp('\\b(' + terms.map(function(t){return t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');}).join('|') + ')\\b', 'g');
  var alreadyWrapped = new Set();

  var walker = document.createTreeWalker(rootEl, NodeFilter.SHOW_TEXT, {
    acceptNode: function(node) {
      if (!node.nodeValue) return NodeFilter.FILTER_REJECT;
      if (node.parentElement && node.parentElement.classList.contains('glossary-term')) return NodeFilter.FILTER_REJECT;
      if (node.parentElement && ['SCRIPT','STYLE','BUTTON'].indexOf(node.parentElement.tagName) >= 0) return NodeFilter.FILTER_REJECT;
      return pattern.test(node.nodeValue) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
    }
  });

  var nodes = [];
  var n;
  while ((n = walker.nextNode())) nodes.push(n);

  nodes.forEach(function(node) {
    var text = node.nodeValue;
    pattern.lastIndex = 0;
    var lastIndex = 0;
    var match;
    var fragment = document.createDocumentFragment();
    while ((match = pattern.exec(text)) !== null) {
      var key = match[1];
      var globalKey = rootEl.id + ':' + key;
      if (alreadyWrapped.has(globalKey)) continue;
      alreadyWrapped.add(globalKey);
      if (match.index > lastIndex) {
        fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
      }
      var span = document.createElement('span');
      span.className = 'glossary-term';
      span.textContent = key;
      span.style.cssText = 'color: var(--primary); border-bottom: 1px dashed var(--primary); cursor: help; font-weight: 600;';
      span.title = 'Click para ver definición';
      span.onclick = function(e) {
        e.stopPropagation();
        window.showGlossaryDefinition(key, e.clientX, e.clientY);
      };
      fragment.appendChild(span);
      lastIndex = pattern.lastIndex;
    }
    if (lastIndex > 0) {
      if (lastIndex < text.length) {
        fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
      }
      node.parentNode.replaceChild(fragment, node);
    }
  });
};

// Muestra un mini-popup con la definición de un término del glosario
window.showGlossaryDefinition = function(term, x, y) {
  var existing = document.getElementById('__glossary_popup');
  if (existing) existing.remove();
  var def = window.TECHNICAL_GLOSSARY[term];
  if (!def) return;
  var popup = document.createElement('div');
  popup.id = '__glossary_popup';
  var left = Math.min(x, window.innerWidth - 340);
  var top = Math.min(y + 12, window.innerHeight - 220);
  popup.style.cssText = 'position:fixed; top:' + top + 'px; left:' + left + 'px; width:22rem; max-width:calc(100vw - 1.5rem); background-color: var(--card); color: var(--foreground); border: 2px solid var(--accent); border-radius: 0.75rem; padding: 0.875rem 1rem; font-size: 0.78rem; line-height: 1.55; box-shadow: 0 30px 60px -15px rgba(0,0,0,0.6), 0 0 0 4px color-mix(in oklch, var(--accent) 18%, transparent); z-index: 100000;';
  popup.innerHTML = '<div style="display:flex; align-items:flex-start; gap:0.5rem;"><div style="font-size: 11px; font-weight: 700; color: var(--accent); text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px;">📖 Glosario</div><button onclick="this.parentElement.parentElement.remove()" style="margin-left:auto; background:transparent; border:none; cursor:pointer; color:var(--muted-foreground); font-size:18px; line-height:1; padding:0 4px;">×</button></div><div style="font-weight:700; color:var(--accent); margin-bottom:6px;">' + term + '</div><div>' + def + '</div>';
  document.body.appendChild(popup);
  // Cerrar al click fuera
  setTimeout(function() {
    var closer = function(e) {
      if (!popup.contains(e.target)) {
        popup.remove();
        document.removeEventListener('click', closer);
      }
    };
    document.addEventListener('click', closer);
  }, 50);
};
