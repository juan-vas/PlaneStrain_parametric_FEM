%% Laminado con Gap central ondulación bezier (C2 quinta + suave + bisección + k común) %%

clear; clc; close all;
fprintf('=== Laminado 2D con GAP central  ===\n');

% ---- Entradas laminado ----
N = input('Número de láminas (entero > 0): ');
if isempty(N) || ~isscalar(N) || N < 1 || N ~= round(N), error('N inválido.'); end

ply_gap = input(sprintf('Índice de lámina que presenta el GAP (1..%d): ', N));
if isempty(ply_gap) || ~isscalar(ply_gap) || ply_gap < 1 || ply_gap > N || ply_gap ~= round(ply_gap)
    error('Índice de lámina con GAP inválido.');
end

g = input('Ancho del GAP [mm] (ejemplo 0.5mm): ');
if isempty(g) || ~isscalar(g) || g <= 0 || g >= 5
    error('Ancho de GAP inválido (0 < g < 5).');
end

% ---- Parámetros geométricos ----
t_ply = 0.125;  W = 5; lw = 1.4; nx = 500;

% ---- Ondulación ----
beta=0.08; alpha=0.55; xc=W/2;  xL=xc-g/2;  xR=xc+g/2;
x = linspace(0, W, nx);

% Ventana coseno
f = zeros(size(x));
idxWin = (x >= xL) & (x <= xR);
f(idxWin) = 0.5*(1 + cos(pi*(x(idxWin) - xc)/(g/2)));

A0    = beta * g;
y_ifc = (0:N) * t_ply;

% Interfaces
Y = zeros(N+1, nx);
for k = 0:N
    if k < ply_gap
        Y(k+1,:) = y_ifc(k+1);
    else
        Ak = A0 * exp(-alpha * (k - ply_gap));
        Y(k+1,:) = y_ifc(k+1) - Ak .* f;
    end
end

%% ---- Unión dentro del gap ----
delta_frac = 0.12;
delta      = min(max(delta_frac*g, 1e-6), 0.49*g);
x_aL       = xL + delta;
x_aR       = xR - delta;

%% ---- Parámetros Bézier del GAP ----
C_gap   = 0.95 * g;      % base de penetración (se escalará con k)
smooth  = 0.30;          % bias vertical 0..1

% Retorno y cierre
return_frac  = 0.85;     % cuánto “vuelve” P4 en x
eps_end_frac = 0.03;     % cola final (misma dirección del retorno)

%% ---- Chequeo anti-intersección ----
tol_clear = 0.002;
npt_bez   = 600;
k_min     = 0.35;
max_iter  = 28;

%% ---- Dibujo ----
figure('Name','Laminado con gap (C2 + smooth + bisección + unión desplazada, CON retorno, k común)','Color','w'); hold on; box on;

% >>>>>>>>> NUEVO: recolector de curvas para exportar
curves = {};  % cada entrada: struct('x',vec,'y',vec)

for i = 1:N
    y_low = Y(i,:);
    y_up  = Y(i+1,:);

    if i == ply_gap
        % Segmentos fuera de la zona de unión
        idxLseg = x <= x_aL;  idxRseg = x >= x_aR;
        if any(idxLseg)
            plot(x(idxLseg), y_low(idxLseg), 'k-', 'LineWidth', lw);
            plot(x(idxLseg), y_up(idxLseg),  'k-', 'LineWidth', lw);
            curves{end+1} = struct('x', x(idxLseg), 'y', y_low(idxLseg)); %#ok<SAGROW>
            curves{end+1} = struct('x', x(idxLseg), 'y', y_up(idxLseg));  %#ok<SAGROW>
        end
        if any(idxRseg)
            plot(x(idxRseg), y_low(idxRseg), 'k-', 'LineWidth', lw);
            plot(x(idxRseg), y_up(idxRseg),  'k-', 'LineWidth', lw);
            curves{end+1} = struct('x', x(idxRseg), 'y', y_low(idxRseg)); %#ok<SAGROW>
            curves{end+1} = struct('x', x(idxRseg), 'y', y_up(idxRseg));  %#ok<SAGROW>
        end

        % Valores en los puntos de unión
        yLa_low = interp1(x, y_low, x_aL);  yLa_up = interp1(x, y_up, x_aL);
        yRa_low = interp1(x, y_low, x_aR);  yRa_up = interp1(x, y_up, x_aR);

        % 1) BISECCIÓN independiente para estimar k_L y k_R
        [~, ~, kL] = bezierEdgeC2_bisec_return(x_aL, yLa_low, yLa_up, +1, C_gap, smooth, ...
                                  x, y_low, y_up, [x_aL xR], tol_clear, npt_bez, k_min, max_iter, ...
                                  return_frac, eps_end_frac);

        [~, ~, kR] = bezierEdgeC2_bisec_return(x_aR, yRa_low, yRa_up, -1, C_gap, smooth, ...
                                  x, y_low, y_up, [xL x_aR], tol_clear, npt_bez, k_min, max_iter, ...
                                  return_frac, eps_end_frac);

        % 2) FORZAR k común (conservador)
        k_common = min(kL, kR);

        % 3) Reconstruir AMBOS bordes con el MISMO k_common
        [xbL, ybL] = bezierEdgeC2_fixedK_return(x_aL, yLa_low, yLa_up, +1, C_gap, k_common, smooth, ...
                                                return_frac, eps_end_frac, x, y_up, npt_bez);

        [xbR, ybR] = bezierEdgeC2_fixedK_return(x_aR, yRa_low, yRa_up, -1, C_gap, k_common, smooth, ...
                                                return_frac, eps_end_frac, x, y_up, npt_bez);

        plot(xbL, ybL, 'k-', 'LineWidth', lw);
        plot(xbR, ybR, 'k-', 'LineWidth', lw);

        % >>>>>>>>> NUEVO: añadir las dos Bézier a exportar
        curves{end+1} = struct('x', xbL, 'y', ybL); %#ok<SAGROW>
        curves{end+1} = struct('x', xbR, 'y', ybR); %#ok<SAGROW>

        % (opcional) ver k's
        fprintf('kL=%.4f, kR=%.4f -> k_common=%.4f\n', kL, kR, k_common);

    else
        plot(x, y_low, 'k-', 'LineWidth', lw);
        plot(x, y_up,  'k-', 'LineWidth', lw);
        % >>>>>>>>> NUEVO: añadir los dos bordes completos a exportar
        curves{end+1} = struct('x', x, 'y', y_low); %#ok<SAGROW>
        curves{end+1} = struct('x', x, 'y', y_up);  %#ok<SAGROW>
    end

    % Cantos verticales
    plot([0 0], [y_low(1) y_up(1)], 'k-', 'LineWidth', lw);
    plot([W W], [y_low(end) y_up(end)], 'k-', 'LineWidth', lw);

    % >>>>>>>>> NUEVO: añadir cantos como mini-curvas (2 puntos)
    curves{end+1} = struct('x', [0, 0], 'y', [y_low(1), y_up(1)]); %#ok<SAGROW>
    curves{end+1} = struct('x', [W, W], 'y', [y_low(end), y_up(end)]); %#ok<SAGROW>
end

H_escala_max = N * (t_ply + 0.0125);
axis([0 W 0 H_escala_max]); axis equal;
xlabel('x [mm]'); ylabel('y [mm]');
title(sprintf('GAP en lámina %d | N=%d | t=%.3f | g=%.3f | α=%.2f | β=%.2f | Δ=%.3f', ...
      ply_gap, N, t_ply, g, alpha, beta, delta));
set(gca,'FontSize',12,'YGrid','on');

%% ====== EXPORTACIÓN MÍNIMA A NASTRAN (sólo GRID) ======
% Escribe un .bdf con todos los nodos de todas las curvas (z=0)
fname_bdf = 'curvas_2D_GRID.bdf';
id_start  = 1;               % cambia si quieres
write_bdf_grids_only(fname_bdf, curves, id_start);
fprintf('> Exportado nodos a %s (formato NASTRAN free-field)\n', fname_bdf);

%% ====================== FUNCIONES ======================

% Pendiente local para tangencia fina
function m = localSlopeAt(xv, yv, xq)
    dy = gradient(yv, xv);
    m  = interp1(xv, dy, xq, 'pchip', 'extrap');
end

% ---- Núcleo: genera la quíntica C2 con retorno, cierre exacto y tangente arriba, SIN "S"
function [xb, yb] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap, s_lo, s_hi, ...
                                              return_frac, eps_end_frac, xgrid, y_up_vec, npt)
    if nargin < 12, npt = 70; end

    % Avance/retorno (forma base)
    c1 = C_gap * (0.65 * s_lo);
    c2 = C_gap * (1.00 * s_lo);
    c3 = C_gap * (0.95 * s_hi);
    c4 = C_gap * (0.75 * s_hi);

    back     = return_frac  * c4;
    tail_len = max(eps_end_frac*C_gap, 0.10*back);

    % Control points iniciales (barriga)
    P0 = [x0,              y0];
    P1 = [x0 + dir*c1,     y0];   % y'(0)=0
    P2 = [x0 + dir*c2,     y0];   % y''(0)=0
    P3 = [x0 + dir*c3,     y1];   % (mantenemos para no tocar la barriga)

    % Cierre exacto y tangente sobre la superior, garantizando x monótono en retorno
    x_end = x0 - dir*(back + tail_len);                 
    y_end = interp1(xgrid, y_up_vec, x_end, 'pchip');   
    m_end = localSlopeAt(xgrid, y_up_vec, x_end);       
    v_end = [-dir, -dir*m_end]; v_end = v_end / max(norm(v_end),eps);
    L_end = 0.75*c4;

    P5 = [x_end, y_end];
    P4 = P5 - L_end * v_end;              % clave: x4 > x5 (lado izq.) / x4 < x5 (lado dcho.)

    % Seguridad: unimodalidad estricta del retorno
    if dir == +1
        P4(1) = max(min(P4(1), P3(1)-1e-9), P5(1)+1e-9);
    else
        P4(1) = min(max(P4(1), P3(1)+1e-9), P5(1)-1e-9);
    end

    % Evalúa Bézier quíntica
    t  = linspace(0,1,npt); u = 1 - t;
    B0 = u.^5; B1 = 5*u.^4.*t; B2 = 10*u.^3.*t.^2;
    B3 = 10*u.^2.*t.^3; B4 = 5*u.*t.^4; B5 = t.^5;
    xb = B0*P0(1)+B1*P1(1)+B2*P2(1)+B3*P3(1)+B4*P4(1)+B5*P5(1);
    yb = B0*P0(2)+B1*P1(2)+B2*P2(2)+B3*P3(2)+B4*P4(2)+B5*P5(2);
end

% ---- Bisección: devuelve también k_best
function [xb_best, yb_best, k_best] = bezierEdgeC2_bisec_return(x0, y0, y1, dir, C_gap, smooth, ...
                                                 xgrid, y_low_vec, y_up_vec, gapLR, tol, npt, k_min, max_iter, ...
                                                 return_frac, eps_end_frac)
    if nargin < 17, eps_end_frac = 0.03; end
    if nargin < 16, return_frac  = 0.85; end
    if nargin < 15, max_iter = 28; end
    if nargin < 14, k_min    = 0.35; end
    if nargin < 13, npt      = 600; end
    tol = max(tol, 0);

    s_lo = 0.55 + 0.35*(1 - smooth);
    s_hi = 0.55 + 0.35*(    smooth);
    s_lo = min(max(s_lo, 0.45), 1.00);
    s_hi = min(max(s_hi, 0.45), 1.00);

    klo = k_min; khi = 1.00;

    [xb_lo, yb_lo] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap*klo, s_lo, s_hi, ...
                                               return_frac, eps_end_frac, xgrid, y_up_vec, npt);
    [ok_lo, ~, ~]  = clearance_ok(xb_lo, yb_lo, xgrid, y_low_vec, y_up_vec, gapLR, tol);

    [xb_hi, yb_hi] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap*khi, s_lo, s_hi, ...
                                               return_frac, eps_end_frac, xgrid, y_up_vec, npt);
    [ok_hi, ~, ~]  = clearance_ok(xb_hi, yb_hi, xgrid, y_low_vec, y_up_vec, gapLR, tol);

    if ~ok_lo && ~ok_hi
        xb_best = xb_lo; yb_best = yb_lo; k_best = klo; return;
    end
    if ok_hi
        xb_best = xb_hi; yb_best = yb_hi; k_best = khi; return;
    end

    for it = 1:max_iter
        km = 0.5*(klo + khi);
        [xb_m, yb_m] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap*km, s_lo, s_hi, ...
                                                 return_frac, eps_end_frac, xgrid, y_up_vec, npt);
        [ok_m, ~, ~] = clearance_ok(xb_m, yb_m, xgrid, y_low_vec, y_up_vec, gapLR, tol);
        if ok_m
            klo = km; xb_lo = xb_m; yb_lo = yb_m;
        else
            khi = km;
        end
        if abs(khi - klo) < 1e-3, break; end
    end
    xb_best = xb_lo; yb_best = yb_lo; k_best = klo;
end

% ---- Generador con k FIJO (para reconstruir con k_common)
function [xb, yb] = bezierEdgeC2_fixedK_return(x0, y0, y1, dir, C_gap, k_fixed, smooth, ...
                                               return_frac, eps_end_frac, xgrid, y_up_vec, npt)
    s_lo = 0.55 + 0.35*(1 - smooth);
    s_hi = 0.55 + 0.35*(    smooth);
    s_lo = min(max(s_lo, 0.45), 1.00);
    s_hi = min(max(s_hi, 0.45), 1.00);
    [xb, yb] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap*k_fixed, s_lo, s_hi, ...
                                         return_frac, eps_end_frac, xgrid, y_up_vec, npt);
end

% ---- Holguras
function [ok, min_low, min_up] = clearance_ok(xb, yb, xgrid, y_low_vec, y_up_vec, gapLR, tol)
    xb = min(max(xb, gapLR(1)), gapLR(2));
    y_low_i = interp1(xgrid, y_low_vec, xb, 'linear');
    y_up_i  = interp1(xgrid, y_up_vec,  xb, 'linear');
    clr_low = yb - y_low_i;
    clr_up  = y_up_i - yb;
    min_low = min(clr_low);
    min_up  = min(clr_up);
    ok = (min_low >= tol) && (min_up >= tol);
end

% ======= NUEVO: escritor mínimo de GRID en .bdf (free-field) =======
function write_bdf_grids_only(fname, curves, id_start)
    if nargin < 3, id_start = 1; end
    fid = fopen(fname,'w');  if fid<0, error('No se pudo abrir %s', fname); end
    %fprintf(fid,'CEND\nBEGIN BULK\n');
    id = id_start;
    for c = 1:numel(curves)
        x = curves{c}.x(:); y = curves{c}.y(:);
        for k = 1:numel(x)
            fprintf(fid,'GRID,%d,0,%.10g,%.10g,0.0\n', id, x(k), y(k));
            id = id + 1;
        end
    end
    % (ENDDATA no es necesario para HyperMesh, pero se puede añadir)
    fclose(fid);
end
