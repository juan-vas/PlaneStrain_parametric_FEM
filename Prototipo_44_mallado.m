%% Laminado con Gap central ondulación bezier (C2 quinta, bisección, k común) %%

clear; clc; close all;
fprintf('=== Laminado 2D con GAP central  ===\n');

% ---- Entradas laminado ----
N = input('Número de láminas (entero > 0): ');
if isempty(N) || ~isscalar(N) || N < 1 || N ~= round(N), error('N inválido.'); end

ply_gap = input(sprintf('Índice de lámina que presenta el GAP (1..%d): ', N));
if isempty(ply_gap) || ~isscalar(ply_gap) || ply_gap < 1 || ply_gap > N || ply_gap ~= round(ply_gap)
    error('Índice de lámina con GAP inválido.');
end

g = input('Ancho del GAP [mm] (ejemplo 0.7mm): ');
if isempty(g) || ~isscalar(g) || g <= 0 || g >= 3
    error('Ancho de GAP inválido (0 < g < 3).');
end

% ---- Parámetros geométricos ----
t_ply = 0.125;  W = 5; lw = 1.4; nx = 400;

% ---- Parámetros para ondulación ----
beta=0.08; alpha=0.55; xc=W/2;  xL=xc-g/2;  xR=xc+g/2;
x = linspace(0, W, nx);

% Función coseno
f = zeros(size(x));
idxWin = (x >= xL) & (x <= xR);
f(idxWin) = 0.5*(1 + cos(pi*(x(idxWin) - xc)/(g/2)));

A0    = beta * g;
y_ifc = (0:N) * t_ply;

%% ---- Interfaces ----
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
delta      = min(max(delta_frac*g, 1e-6), 0.40*g); 
x_aL       = xL + delta;
x_aR       = xR - delta;

%% ---- Parámetros Bézier del GAP ----
C_gap   = 0.95 * g;
smooth  = 0.30;
return_frac  = 0.85;
eps_end_frac = 0.03;

%% ---- Chequeo anti-intersección ----
tol_clear = 0.002;
npt_bez   = 300;
k_min     = 0.35;
max_iter  = 28;

%% ---- Dibujo ----
figure('Name','Laminado con gap','Color','w'); hold on; box on;

% Grosor para internas (1/3 del grosor de contornos)
lw_in = (1/3) * lw;

% Tamaño de marcador de nodos (pequeño)
ms_node = 2;

for i = 1:N
    y_low = Y(i,:);
    y_up  = Y(i+1,:);

    if i == ply_gap
        % ====== LÁMINA DEL GAP ======
        idxLseg = x <= x_aL;  
        idxRseg = x >= x_aR;
        if any(idxLseg)
            plot(x(idxLseg), y_low(idxLseg), 'k-', 'LineWidth', lw);
            plot(x(idxLseg), y_up(idxLseg),  'k-', 'LineWidth', lw);
        end
        if any(idxRseg)
            plot(x(idxRseg), y_low(idxRseg), 'k-', 'LineWidth', lw);
            plot(x(idxRseg), y_up(idxRseg),  'k-', 'LineWidth', lw);
        end

        % Interpolación en los puntos de unión
        yLa_low = interp1(x, y_low, x_aL);  yLa_up = interp1(x, y_up, x_aL); 
        yRa_low = interp1(x, y_low, x_aR);  yRa_up = interp1(x, y_up, x_aR);

        % 1) BISECCIÓN para k_L y k_R
        [~, ~, kL] = bezierEdgeC2_bisec_return(x_aL, yLa_low, yLa_up, +1, C_gap, smooth, ...
                                  x, y_low, y_up, [x_aL xR], tol_clear, npt_bez, k_min, max_iter, ...
                                  return_frac, eps_end_frac);

        [~, ~, kR] = bezierEdgeC2_bisec_return(x_aR, yRa_low, yRa_up, -1, C_gap, smooth, ...
                                  x, y_low, y_up, [xL x_aR], tol_clear, npt_bez, k_min, max_iter, ...
                                  return_frac, eps_end_frac);

        % 2) k común
        k_common = min(kL, kR);

        % 3) Bézier de contornos
        [xbL, ybL] = bezierEdgeC2_fixedK_return(x_aL, yLa_low, yLa_up, +1, C_gap, k_common, smooth, ...
                                                return_frac, eps_end_frac, x, y_up, npt_bez);
        [xbR, ybR] = bezierEdgeC2_fixedK_return(x_aR, yRa_low, yRa_up, -1, C_gap, k_common, smooth, ...
                                                return_frac, eps_end_frac, x, y_up, npt_bez);
        plot(xbL, ybL, 'k-', 'LineWidth', lw);
        plot(xbR, ybR, 'k-', 'LineWidth', lw);

        % === Líneas internas rectas
        y_int1 = y_ifc(i) + (1/4) * t_ply;
        plot([0, x_aL], [y_int1, y_int1], 'k-', 'LineWidth', lw_in);
        plot([x_aR, W], [y_int1, y_int1], 'k-', 'LineWidth', lw_in);
        x_end_L_full = bezier_xend(x_aL, +1, C_gap, k_common, smooth, return_frac, eps_end_frac);
        x_end_R_full = bezier_xend(x_aR, -1, C_gap, k_common, smooth, return_frac, eps_end_frac);
        x_end_L = x_aL - 0.5*(x_aL - x_end_L_full);
        x_end_R = x_aR - 0.5*(x_aR - x_end_R_full);
        y_int2 = y_ifc(i) + (2/3) * t_ply;
        plot([0, x_end_L], [y_int2, y_int2], 'k-', 'LineWidth', lw_in);
        plot([x_end_R, W], [y_int2, y_int2], 'k-', 'LineWidth', lw_in);

        % === Bézier interna (entre y_int1 y y_int2), escalada
        C_gap_int = 0.5 * C_gap;
        y_up_int  = y_int2 * ones(size(x));
        [xbiL, ybiL] = bezierEdgeC2_fixedK_return(x_aL, y_int1, y_int2, +1, C_gap_int, k_common, smooth, ...
                                                  return_frac, eps_end_frac, x, y_up_int, npt_bez);
        [xbiR, ybiR] = bezierEdgeC2_fixedK_return(x_aR, y_int1, y_int2, -1, C_gap_int, k_common, smooth, ...
                                                  return_frac, eps_end_frac, x, y_up_int, npt_bez);
        plot(xbiL, ybiL, 'k-', 'LineWidth', lw_in);
        plot(xbiR, ybiR, 'k-', 'LineWidth', lw_in);

        % === Línea interna recta entre extremos interiores de Bézier exteriores
        [~, iMaxL] = max(xbL);  xL_ext = xbL(iMaxL);  yL_ext = ybL(iMaxL);
        [~, iMinR] = min(xbR);  xR_ext = xbR(iMinR);  yR_ext = ybR(iMinR);
        plot([xL_ext, xR_ext], [yL_ext, yR_ext], 'k-', 'LineWidth', lw_in);

        % === Verticales guía (desde base hasta Bézier exterior superior)
        xvL_conn = xbiL(end);  % conexión superior interna izquierda
        xvR_conn = xbiR(end);  % conexión superior interna derecha

        % izquierda: cortes con exterior
        ycutsL = [];
        for kk = 1:numel(xbL)-1
            x1 = xbL(kk); x2 = xbL(kk+1);
            if (x1 - xvL_conn)*(x2 - xvL_conn) <= 0
                if x2 ~= x1
                    tloc = (xvL_conn - x1)/(x2 - x1);
                    ycutsL(end+1) = ybL(kk) + tloc*(ybL(kk+1) - ybL(kk)); %#ok<AGROW>
                else
                    ycutsL(end+1) = ybL(kk); ycutsL(end+1) = ybL(kk+1); %#ok<AGROW>
                end
            end
        end
        if ~isempty(ycutsL)
            ycutsL = uniquetol(ycutsL,1e-12);
            plot([xvL_conn xvL_conn],[y_ifc(i) max(ycutsL)],'k-','LineWidth',lw_in);
        end
        % derecha: cortes con exterior
        ycutsR = [];
        for kk = 1:numel(xbR)-1
            x1 = xbR(kk); x2 = xbR(kk+1);
            if (x1 - xvR_conn)*(x2 - xvR_conn) <= 0
                if x2 ~= x1
                    tloc = (xvR_conn - x1)/(x2 - x1);
                    ycutsR(end+1) = ybR(kk) + tloc*(ybR(kk+1) - ybR(kk)); %#ok<AGROW>
                else
                    ycutsR(end+1) = ybR(kk); ycutsR(end+1) = ybR(kk+1); %#ok<AGROW>
                end
            end
        end
        if ~isempty(ycutsR)
            ycutsR = uniquetol(ycutsR,1e-12);
            plot([xvR_conn xvR_conn],[y_ifc(i) max(ycutsR)],'k-','LineWidth',lw_in);
        end

        % ==================================================================
        % === NODOS EN y_target = y_ifc(i) + 0.4*t_ply  (AMBOS LADOS)
        y_target = y_ifc(i) + 0.4 * t_ply;

        % Intersecciones con Bézier interna IZQUIERDA (y=y_target) -> usar la de mayor x
        xintsL = [];
        for kk = 1:numel(ybiL)-1
            y1 = ybiL(kk); y2 = ybiL(kk+1);
            if (y1 - y_target)*(y2 - y_target) <= 0
                if y2 ~= y1
                    tloc = (y_target - y1)/(y2 - y1);
                    xintsL(end+1) = xbiL(kk) + tloc*(xbiL(kk+1) - xbiL(kk)); %#ok<AGROW>
                else
                    xintsL(end+1) = xbiL(kk); xintsL(end+1) = xbiL(kk+1); %#ok<AGROW>
                end
            end
        end
        if ~isempty(xintsL)
            x_int_L = max(xintsL); % la más interior
            x_nodesL = linspace(xvL_conn, x_int_L, 5);
            y_nodesL = y_target * ones(size(x_nodesL));
            plot(x_nodesL, y_nodesL, 'ko', 'MarkerFaceColor','k', 'MarkerSize', ms_node);
        end

        % Intersecciones con Bézier interna DERECHA (y=y_target) -> usar la de menor x
        xintsR = [];
        for kk = 1:numel(ybiR)-1
            y1 = ybiR(kk); y2 = ybiR(kk+1);
            if (y1 - y_target)*(y2 - y_target) <= 0
                if y2 ~= y1
                    tloc = (y_target - y1)/(y2 - y1);
                    xintsR(end+1) = xbiR(kk) + tloc*(xbiR(kk+1) - xbiR(kk)); %#ok<AGROW>
                else
                    xintsR(end+1) = xbiR(kk); xintsR(end+1) = xbiR(kk+1); %#ok<AGROW>
                end
            end
        end
        if ~isempty(xintsR)
            x_int_R = min(xintsR); % la más interior
            x_nodesR = linspace(x_int_R, xvR_conn, 5);
            y_nodesR = y_target * ones(size(x_nodesR));
            plot(x_nodesR, y_nodesR, 'ko', 'MarkerFaceColor','k', 'MarkerSize', ms_node);
        end
        % ==================================================================

    else
        % ====== LÁMINA SIN GAP ======
        tvals = [0, 1/3, 2/3, 1];
        for tt = 1:numel(tvals)
            t = tvals(tt);
            if i <= ply_gap
                y_line = y_low + t .* (y_up - y_low);
            else
                y_base = y_ifc(i) + t * t_ply;
                k_eff  = (i - 1) + t;
                Ak_t   = A0 * exp(-alpha * (k_eff - ply_gap));
                y_line = y_base - Ak_t .* f;
            end
            if (t==0) || (t==1)
                plot(x, y_line, 'k-', 'LineWidth', lw);
            else
                plot(x, y_line, 'k-', 'LineWidth', lw_in);
            end
        end
    end

    % Verticales de contorno
    plot([0 0], [y_low(1) y_up(1)], 'k-', 'LineWidth', lw);
    plot([W W], [y_low(end) y_up(end)], 'k-', 'LineWidth', lw);
end

H_escala_max = N * (t_ply + 0.0125);
axis([0 W 0 H_escala_max]); 
axis equal;
xlabel('x [mm]'); ylabel('y [mm]');
title(sprintf('GAP en lámina %d | N=%d | t=%.3f | g=%.3f | α=%.2f | β=%.2f ', ...
      ply_gap, N, t_ply, g, alpha, beta));
set(gca,'FontSize',12,'YGrid','on');

%% ====================== FUNCIONES ======================

function x_end = bezier_xend(x0, dir, C_gap, k_fixed, smooth, return_frac, eps_end_frac)
    s_hi = 0.55 + 0.35*(smooth);
    s_hi = min(max(s_hi, 0.45), 1.00);
    C = C_gap * k_fixed;
    c4 = C * (0.75 * s_hi);
    back     = return_frac  * c4;
    tail_len = max(eps_end_frac*C, 0.10*back);
    x_end = x0 - dir*(back + tail_len);
end

function m = localSlopeAt(xv, yv, xq)
    dy = gradient(yv, xv);
    m  = interp1(xv, dy, xq, 'pchip', 'extrap');
end

function [xb, yb] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap, s_lo, s_hi, ...
                                              return_frac, eps_end_frac, xgrid, y_up_vec, npt)
    if nargin < 12, npt = 70; end
    c1 = C_gap * (0.65 * s_lo);
    c2 = C_gap * (1.00 * s_lo);
    c3 = C_gap * (0.95 * s_hi);
    c4 = C_gap * (0.75 * s_hi);
    back     = return_frac  * c4;
    tail_len = max(eps_end_frac*C_gap, 0.10*back);
    P0 = [x0,              y0];
    P1 = [x0 + dir*c1,     y0];
    P2 = [x0 + dir*c2,     y0];
    P3 = [x0 + dir*c3,     y1];
    x_end = x0 - dir*(back + tail_len);                 
    y_end = interp1(xgrid, y_up_vec, x_end, 'pchip');   
    m_end = localSlopeAt(xgrid, y_up_vec, x_end);       
    v_end = [-dir, -dir*m_end]; v_end = v_end / max(norm(v_end),eps);
    L_end = 0.75*c4;
    P5 = [x_end, y_end];
    P4 = P5 - L_end * v_end;
    if dir == +1
        P4(1) = max(min(P4(1), P3(1)-1e-9), P5(1)+1e-9);
    else
        P4(1) = min(max(P4(1), P3(1)+1e-9), P5(1)-1e-9);
    end
    t  = linspace(0,1,npt); u = 1 - t;
    B0 = u.^5; B1 = 5*u.^4.*t; B2 = 10*u.^3.*t.^2;
    B3 = 10*u.^2.*t.^3; B4 = 5*u.*t.^4; B5 = t.^5;
    xb = B0*P0(1)+B1*P1(1)+B2*P2(1)+B3*P3(1)+B4*P4(1)+B5*P5(1);
    yb = B0*P0(2)+B1*P1(2)+B2*P2(2)+B3*P3(2)+B4*P4(2)+B5*P5(2);
end

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
        if ok_m, klo = km; else, khi = km; end
        if abs(khi - klo) < 1e-3, break; end
    end
    [xb_best, yb_best] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap*klo, s_lo, s_hi, ...
                                                   return_frac, eps_end_frac, xgrid, y_up_vec, npt);
    k_best = klo;
end

function [xb, yb] = bezierEdgeC2_fixedK_return(x0, y0, y1, dir, C_gap, k_fixed, smooth, ...
                                               return_frac, eps_end_frac, xgrid, y_up_vec, npt)
    s_lo = 0.55 + 0.35*(1 - smooth);
    s_hi = 0.55 + 0.35*(    smooth);
    s_lo = min(max(s_lo, 0.45), 1.00);
    s_hi = min(max(s_hi, 0.45), 1.00);
    [xb, yb] = bezierEdgeC2scaled_return(x0, y0, y1, dir, C_gap*k_fixed, s_lo, s_hi, ...
                                         return_frac, eps_end_frac, xgrid, y_up_vec, npt);
end

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

