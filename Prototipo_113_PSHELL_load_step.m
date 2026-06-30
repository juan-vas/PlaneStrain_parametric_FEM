%% Laminado con Gap central ondulación bezier (C2 quinta, bisección, k común) %%
% Versión determinista + proyección + poda de nodos normales en el ancho de gap
% - Frontera GAP e interior: IDs fijos (85000+, 99000+)
% - Proyección (verticales y bordes): IDs 100000+
% - PODA: eliminar nodes_ext (IDs desde 1) con x en [xvL, xvR] y elementos que los usen

clear; clc; close all;
fprintf('=== Laminado 2D con GAP central  (Determinista + Proyección + Poda) ===\n');

% ---- Selección de apilado (packs simétricos y equilibrados) ----
[theta_vec, layup_label] = ask_apilado_pack();
N = numel(theta_vec);                         % nº de láminas implícito
fprintf('> Apilado elegido: %s | N = %d láminas\n', layup_label, N);

% Con N conocido, ahora sí pedimos la lámina del GAP y el ancho g
ply_gap = input(sprintf('Índice de lámina que presenta el GAP (1..%d): ', N));
if isempty(ply_gap) || ~isscalar(ply_gap) || ply_gap < 1 || ply_gap > N || ply_gap ~= round(ply_gap)
    error('Índice de lámina con GAP inválido.');
end

g = input('Ancho del GAP [mm] (ejemplo 0.7mm): ');
if isempty(g) || ~isscalar(g) || g <= 0 || g >= 3
    error('Ancho de GAP inválido (0 < g < 3).');
end

% ---- Parámetros geométricos ----
t_ply = 0.125;  W =6; lw = 1.5; nx = 400;

% ---- Parámetros para ondulación ----
beta=0.05; alpha=0.55; xc=W/2;  xL=xc-g/2;  xR=xc+g/2;
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
delta_frac = 0.10;
delta      = min(max(delta_frac*g, 1e-6), 0.30*g);
x_aL       = xL + delta;
x_aR       = xR - delta;

%% ---- Parámetros Bézier del GAP ----
C_gap   = 0.85 * g;
smooth  = 0.30;
return_frac  = 0.75;
eps_end_frac = 0.03;

%% ---- Chequeo anti-intersección ----
tol_clear = 0.002;
npt_bez   = 300;
k_min     = 0.35;
max_iter  = 28;

%% ---- Dibujo ----
figure('Name','Laminado con gap','Color','w'); hold on; box on;

lw_in = 0.1 * lw; % internas

% Variables a reutilizar en mallado/BDF
xbL=[]; ybL=[]; xbR=[]; ybR=[]; xbiL=[]; ybiL=[]; xbiR=[]; ybiR=[];
xvL_conn = NaN; xvR_conn = NaN;

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

        % 3) Bézier EXTERIORES
        [xbL, ybL] = bezierEdgeC2_fixedK_return(x_aL, yLa_low, yLa_up, +1, C_gap, k_common, smooth, ...
                                                return_frac, eps_end_frac, x, y_up, npt_bez);
        [xbR, ybR] = bezierEdgeC2_fixedK_return(x_aR, yRa_low, yRa_up, -1, C_gap, k_common, smooth, ...
                                                return_frac, eps_end_frac, x, y_up, npt_bez);
        plot(xbL, ybL, 'k-', 'LineWidth', lw);
        plot(xbR, ybR, 'k-', 'LineWidth', lw);

        % Extremos interiores (x de las verticales)
        xvL_conn = xbL(end);
        xvR_conn = xbR(end);

        % === Líneas internas rectas (solo visual)
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

        % === Bézier INTERNAS (solo dibujo)
        C_gap_int = 0.5 * C_gap;
        y_up_int  = y_int2 * ones(size(x));
        [xbiL, ybiL] = bezierEdgeC2_fixedK_return(x_aL, y_int1, y_int2, +1, C_gap_int, k_common, smooth, ...
                                                  return_frac, eps_end_frac, x, y_up_int, npt_bez);
        [xbiR, ybiR] = bezierEdgeC2_fixedK_return(x_aR, y_int1, y_int2, -1, C_gap_int, k_common, smooth, ...
                                                  return_frac, eps_end_frac, x, y_up_int, npt_bez);
        plot(xbiL, ybiL, 'k-', 'LineWidth', lw_in);
        plot(xbiR, ybiR, 'k-', 'LineWidth', lw_in);

        % === Línea interna recta entre puntas (solo visual)
        [~, iMaxL] = max(xbL);  xL_tip = xbL(iMaxL);  yL_tip = ybL(iMaxL);
        [~, iMinR] = min(xbR);  xR_tip = xbR(iMinR);  yR_tip = ybR(iMinR);
        plot([xL_tip, xR_tip], [yL_tip, yR_tip], 'k-', 'LineWidth', lw_in);

        % === Verticales guía (solo visual)
        yvL_top = interp1(x, y_up, xvL_conn, 'pchip');
        yvR_top = interp1(x, y_up, xvR_conn, 'pchip');
        plot([xvL_conn xvL_conn],[y_ifc(i) yvL_top],'k-','LineWidth',lw_in);
        plot([xvR_conn xvR_conn],[y_ifc(i) yvR_top],'k-','LineWidth',lw_in);

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

%% ====================== BLOQUE MALLA + BDF (Determinista + Proyección) ======================
nx_mesh = 130;                         
xg = linspace(0, W, nx_mesh);

% Interfaces en malla xg
fg = zeros(size(xg)); fg((xg>=xL)&(xg<=xR)) = 0.5*(1 + cos(pi*(xg((xg>=xL)&(xg<=xR)) - xc)/(g/2)));
Yg = zeros(N+1, nx_mesh);
for k = 0:N
    if k < ply_gap
        Yg(k+1,:) = y_ifc(k+1);
    else
        Ak = A0 * exp(-alpha * (k - ply_gap));
        Yg(k+1,:) = y_ifc(k+1) - Ak .* fg;
    end
end

% ---- util de solape en X ----
overlapX = @(a1,a2,b1,b2) max(a1,b1) <= min(a2,b2);

% Filas de malla (de abajo a arriba) — SOLO para exterior
rows = struct('ply',{},'t',{},'y',{}); 
rows(end+1) = struct('ply',0,'t',0,'y',Yg(1,:));
for i=1:N
    if i==ply_gap
        rows(end+1) = struct('ply',i,'t',0.25,'y',(y_ifc(i)+0.25*t_ply)*ones(1,nx_mesh));
        rows(end+1) = struct('ply',i,'t',2/3 ,'y',(y_ifc(i)+2/3*t_ply)*ones(1,nx_mesh));
    else
        for tt=[1/3 2/3]
            if i <= ply_gap
                y_line = Yg(i,:) + tt.*(Yg(i+1,:) - Yg(i,:));
            else
                y_base = y_ifc(i) + tt*t_ply;
                k_eff  = (i - 1) + tt;
                Ak_t   = A0 * exp(-alpha * (k_eff - ply_gap));
                y_line = y_base - Ak_t .* fg;
            end
            rows(end+1) = struct('ply',i,'t',tt,'y',y_line);
        end
    end
    rows(end+1) = struct('ply',i,'t',1,'y',Yg(i+1,:));
end

% ===== Nodos =====
nodes_ext  = []; next_ext  = 1;          % exterior (IDs libres)
nodes_bdr  = []; next_bdr  = 85000;      % frontera GAP (IDs fijos)
nodes_int  = []; next_int  = 99000;      % interior GAP (IDs fijos)
nodes_proj = []; next_proj = 100000;     % proyectados (IDs fijos)

% ---------- Identificar filas clave ----------
r_bottom = find(arrayfun(@(r) r.ply==ply_gap-1 && abs(r.t-1)<1e-12, rows), 1, 'first'); % frontera inferior
r_below  = find(arrayfun(@(r) r.ply==ply_gap-1 && abs(r.t-2/3)<1e-12, rows), 1, 'first'); % tira inferior (arriba)
r_top    = find(arrayfun(@(r) r.ply==ply_gap   && abs(r.t-1)<1e-12, rows), 1, 'first'); % frontera superior
r_above  = find(arrayfun(@(r) r.ply==ply_gap+1 && abs(r.t-1/3)<1e-12, rows), 1, 'first'); % tira superior (abajo)

% ---------- EXTERIOR por filas ----------
rowID = nan(numel(rows), nx_mesh);
xLspan = @(xj) (~isnan(xvL_conn) && ~isnan(xvR_conn) && xj>=min(xvL_conn,xvR_conn)-1e-12 && xj<=max(xvL_conn,xvR_conn)+1e-12);

for r=1:numel(rows)
    yr = rows(r).y; iply = rows(r).ply; tval = rows(r).t;
    is_bottom_frontier_row = (~isempty(r_bottom) && r==r_bottom);
    is_top_frontier_row    = (~isempty(r_top)    && r==r_top);

    for j=1:nx_mesh
        xj = xg(j); yj = yr(j);

        % 1) Vaciar interior del ply del GAP en líneas intermedias (t<1) dentro [xvL,xvR]
        is_gap_span_mid = (iply==ply_gap) && (tval<1) && xLspan(xj);

        % 2) NO crear nodos exteriores en las filas frontera bottom/top dentro [xvL,xvR]
        is_forbidden_frontier = ((is_bottom_frontier_row || is_top_frontier_row) && xLspan(xj));

        if ~(is_gap_span_mid || is_forbidden_frontier)
            nodes_ext(end+1,:) = [next_ext, xj, yj, 0];
            rowID(r,j) = next_ext; next_ext = next_ext + 1;
        else
            rowID(r,j) = NaN;
        end
    end
end

% ===== Geometría clave del GAP =====
y_bottom = y_ifc(ply_gap);
y_top_L  = interp1(xg, Yg(ply_gap+1,:), xvL_conn, 'linear','extrap');
y_top_R  = interp1(xg, Yg(ply_gap+1,:), xvR_conn, 'linear','extrap');

% ===== Conteos fijos =====
Nvert = 8; Nbot = 24; Ntop = 24;
Nbx   = 20; Nbi  = 20; Nh = 10; NdiscL = 5; NdiscR = 5;
NbridgeL_low=4; NbridgeL_up=3; NbridgeR_low=3; NbridgeR_up=2;

% ================== FRONTERA GAP (nodes_bdr) ==================
yL_vec = linspace(y_bottom, y_top_L, Nvert);
for k=1:Nvert, nodes_bdr(end+1,:) = [next_bdr, xvL_conn, yL_vec(k), 0]; next_bdr=next_bdr+1; end

xb_bot = linspace(xvL_conn, xvR_conn, Nbot+2); xb_bot = xb_bot(2:end-1);
for k=1:Nbot, nodes_bdr(end+1,:) = [next_bdr, xb_bot(k), y_bottom, 0]; next_bdr=next_bdr+1; end

xt_top = linspace(xvL_conn, xvR_conn, Ntop+2); xt_top = xt_top(2:end-1);
yt_top = interp1(xg, Yg(ply_gap+1,:), xt_top, 'linear','extrap');
for k=1:Ntop, nodes_bdr(end+1,:) = [next_bdr, xt_top(k), yt_top(k), 0]; next_bdr=next_bdr+1; end

yR_vec = linspace(y_bottom, y_top_R, Nvert);
for k=1:Nvert, nodes_bdr(end+1,:) = [next_bdr, xvR_conn, yR_vec(k), 0]; next_bdr=next_bdr+1; end

% ================== INTERIOR GAP (nodes_int) ==================
iL_ext = round(linspace(1, numel(xbL), Nbx));
iR_ext = round(linspace(1, numel(xbR), Nbx));
for p=1:Nbx, nodes_int(end+1,:)=[next_int, xbL(iL_ext(p)), ybL(iL_ext(p)), 0]; next_int=next_int+1; end
for p=1:Nbx, nodes_int(end+1,:)=[next_int, xbR(iR_ext(p)), ybR(iR_ext(p)), 0]; next_int=next_int+1; end

iL_int = round(linspace(1, numel(xbiL), Nbi));
iR_int = round(linspace(1, numel(xbiR), Nbi));
for p=1:Nbi, nodes_int(end+1,:)=[next_int, xbiL(iL_int(p)), ybiL(iL_int(p)), 0]; next_int=next_int+1; end
for p=1:Nbi, nodes_int(end+1,:)=[next_int, xbiR(iR_int(p)), ybiR(iR_int(p)), 0]; next_int=next_int+1; end

[~, iMaxL_tip] = max(xbL);  xL_tip = xbL(iMaxL_tip);
[~, iMinR]     = min(xbR);  xR_tip = xbR(iMinR);
if Nh>0
    xh = linspace(xL_tip, xR_tip, Nh+2); xh = xh(2:end-1);
    y_h = y_ifc(ply_gap) + 0.25*t_ply;
    for j=1:numel(xh), nodes_int(end+1,:)=[next_int, xh(j), y_h, 0]; next_int=next_int+1; end
end

y_target = y_ifc(ply_gap) + 0.4 * t_ply;
x_int_L = get_x_at_y_on_curve(xbiL, ybiL, y_target, 'max');
x_int_R = get_x_at_y_on_curve(xbiR, ybiR, y_target, 'min');
if isnan(x_int_L) || ~isfinite(x_int_L), x_int_L = xvL_conn + 0.3*(xR_tip - xvL_conn); end
if isnan(x_int_R) || ~isfinite(x_int_R), x_int_R = xvR_conn - 0.3*(xvR_conn - xL_tip); end
x_nodesL = linspace(xvL_conn, x_int_L, NdiscL+2); x_nodesL = x_nodesL(2:end-1);
x_nodesR = linspace(x_int_R, xvR_conn, NdiscR+2); x_nodesR = x_nodesR(2:end-1);
for j=1:numel(x_nodesL), nodes_int(end+1,:)=[next_int, x_nodesL(j), y_target, 0]; next_int=next_int+1; end
for j=1:numel(x_nodesR), nodes_int(end+1,:)=[next_int, x_nodesR(j), y_target, 0]; next_int=next_int+1; end

if NbridgeL_low>0
    xs = linspace(xvL_conn, xbiL(1), NbridgeL_low+2); xs = xs(2:end-1);
    for k=1:NbridgeL_low, nodes_int(end+1,:)=[next_int, xs(k), ybiL(1), 0]; next_int=next_int+1; end
end
if NbridgeL_up>0
    xs = linspace(xbiL(end), xvL_conn, NbridgeL_up+2); xs = xs(2:end-1);
    for k=1:NbridgeL_up, nodes_int(end+1,:)=[next_int, xs(k), ybiL(end), 0]; next_int=next_int+1; end
end
if NbridgeR_low>0
    xs = linspace(xvR_conn, xbiR(1), NbridgeR_low+2); xs = xs(2:end-1);
    for k=1:NbridgeR_low, nodes_int(end+1,:)=[next_int, xs(k), ybiR(1), 0]; next_int=next_int+1; end
end
if NbridgeR_up>0
    xs = linspace(xbiR(end), xvR_conn, NbridgeR_up+2); xs = xs(2:end-1);
    for k=1:NbridgeR_up, nodes_int(end+1,:)=[next_int, xs(k), ybiR(end), 0]; next_int=next_int+1; end
end

% ================== PROYECCIÓN VERTICAL (nodos 100000+) ==================
% filas por debajo (incluye r_below si existe)
if ~isempty(r_bottom)
    if ~isempty(r_below), rows_below = r_below:-1:1; else, rows_below = (r_bottom-1):-1:1; end
else
    rows_below = [];
end
% filas por encima (incluye r_above si existe)
if ~isempty(r_top)
    if ~isempty(r_above), rows_above = r_above:1:numel(rows); else, rows_above = (r_top+1):1:numel(rows); end
else
    rows_above = [];
end
nbelow = numel(rows_below);
nabove = numel(rows_above);

% mapeos de posición por fila
pos_below = zeros(1,numel(rows)); for ii=1:nbelow, pos_below(rows_below(ii)) = ii; end
pos_above = zeros(1,numel(rows)); for ii=1:nabove, pos_above(rows_above(ii)) = ii; end

% Arrays para guardar IDs proyectados por estructura:
proj_bot_ids = zeros(nbelow, Nbot);     % [fila_below, k=1..Nbot]  (debajo bottom)
proj_top_ids = zeros(nabove, Ntop);     % [fila_above, k=1..Ntop]  (encima top)
vl_below = zeros(nbelow,1); vr_below = zeros(nbelow,1);  % verticales en filas below
vl_above = zeros(nabove,1); vr_above = zeros(nabove,1);  % verticales en filas above

% Proyección inferior → abajo (guardando IDs)
for ii = 1:nbelow
    rr = rows_below(ii);
    yrow = rows(rr).y;
    for k=1:numel(xb_bot)
        xp = xb_bot(k);
        yp = interp1(xg, yrow, xp, 'linear','extrap');
        nodes_proj(end+1,:) = [next_proj, xp, yp, 0];
        proj_bot_ids(ii,k)  = next_proj;
        next_proj = next_proj + 1;
    end
end

% Proyección superior → arriba (guardando IDs)
for ii = 1:nabove
    rr = rows_above(ii);
    yrow = rows(rr).y;
    for k=1:numel(xt_top)
        xp = xt_top(k);
        yp = interp1(xg, yrow, xp, 'linear','extrap');
        nodes_proj(end+1,:) = [next_proj, xp, yp, 0];
        proj_top_ids(ii,k)  = next_proj;
        next_proj = next_proj + 1;
    end
end

% Proyección de verticales (evitar filas internas del gap y filas frontera)
for rr = 1:numel(rows)
    iply = rows(rr).ply; tval = rows(rr).t;
    if (iply==ply_gap) && (tval<1), continue; end
    if (~isempty(r_bottom) && rr==r_bottom) || (~isempty(r_top) && rr==r_top)
        continue;
    end
    yrow = rows(rr).y;
    if ~isnan(xvL_conn)
        ypL = interp1(xg, yrow, xvL_conn, 'linear','extrap');
        nodes_proj(end+1,:) = [next_proj, xvL_conn, ypL, 0];
        pb = pos_below(rr); if pb>0, vl_below(pb) = next_proj; end
        pa = pos_above(rr); if pa>0, vl_above(pa) = next_proj; end
        next_proj = next_proj + 1;
    end
    if ~isnan(xvR_conn)
        ypR = interp1(xg, yrow, xvR_conn, 'linear','extrap');
        nodes_proj(end+1,:) = [next_proj, xvR_conn, ypR, 0];
        pb = pos_below(rr); if pb>0, vr_below(pb) = next_proj; end
        pa = pos_above(rr); if pa>0, vr_above(pa) = next_proj; end
        next_proj = next_proj + 1;
    end
end

% ================== ELEMENTOS CQUAD4 fuera del GAP (malla exterior normal) ==================
elems = [];          % CQUAD4: [EID, PID, n1, n2, n3, n4]
elems_tri = [];      % CTRIA3 : [EID, PID, n1, n2, n3]
next_eid = 1; PID = 1;

have_bottom_band = ~isempty(r_below) && ~isempty(r_bottom);
have_top_band    = ~isempty(r_top)   && ~isempty(r_above);

for r=1:(numel(rows)-1)
    ids_bot = rowID(r,:); ids_top = rowID(r+1,:);

    skip_inferior_subspan = have_bottom_band && (r==r_below && r+1==r_bottom);
    skip_superior_subspan = have_top_band    && (r==r_top   && r+1==r_above);

    for j=1:(nx_mesh-1)
        n1=ids_bot(j); n2=ids_bot(j+1); n3=ids_top(j+1); n4=ids_top(j);
        if any(isnan([n1 n2 n3 n4])), continue; end

        cell_over_gap = ~isnan(xvL_conn) && ~isnan(xvR_conn) && overlapX(xg(j),xg(j+1), min(xvL_conn,xvR_conn), max(xvL_conn,xvR_conn));

        if (skip_inferior_subspan || skip_superior_subspan) && cell_over_gap
            continue;
        end

        elems(end+1,:) = [next_eid, PID, n1, n2, n3, n4]; next_eid=next_eid+1;
    end
end

%% === ELEMENTOS: bandas de proyectados (bajo bottom y sobre top) ===
% Debajo del bottom
if nbelow >= 2 && ~isempty(proj_bot_ids)
    for ii = 1:(nbelow-1)
        ids_low = proj_bot_ids(ii+1,:);   % fila más baja
        ids_up  = proj_bot_ids(ii,:);     % fila inmediatamente superior
        for k = 1:(size(proj_bot_ids,2)-1)
            n1 = ids_low(k); n2 = ids_low(k+1); n3 = ids_up(k+1); n4 = ids_up(k);
            if all([n1 n2 n3 n4] > 0)
                elems(end+1,:) = [next_eid, PID, n1, n2, n3, n4]; next_eid=next_eid+1;
            end
        end
    end
end
% Encima del top
if nabove >= 2 && ~isempty(proj_top_ids)
    for ii = 1:(nabove-1)
        ids_low = proj_top_ids(ii,:);     
        ids_up  = proj_top_ids(ii+1,:);   
        for k = 1:(size(proj_top_ids,2)-1)
            n1 = ids_low(k); n2 = ids_low(k+1); n3 = ids_up(k+1); n4 = ids_up(k);
            if all([n1 n2 n3 n4] > 0)
                elems(end+1,:) = [next_eid, PID, n1, n2, n3, n4]; next_eid=next_eid+1;
            end
        end
    end
end

%% === ELEMENTOS: columnas junto a verticales con nodos proyectados ===
% Debajo del bottom
if nbelow >= 2 && ~isempty(proj_bot_ids)
    for ii = 1:(nbelow-1)
        % izquierda (xvL con columna k=1)
        v_low  = vl_below(ii+1);   v_up  = vl_below(ii);
        c_low  = proj_bot_ids(ii+1, 1); c_up  = proj_bot_ids(ii, 1);
        if all([v_low,v_up,c_low,c_up] > 0)
            elems(end+1,:) = [next_eid, PID, v_low, c_low, c_up, v_up]; next_eid=next_eid+1;
        end
        % derecha (columna k=end con xvR)
        c_low  = proj_bot_ids(ii+1, end); c_up  = proj_bot_ids(ii, end);
        v_low  = vr_below(ii+1);         v_up  = vr_below(ii);
        if all([c_low,c_up,v_low,v_up] > 0)
            elems(end+1,:) = [next_eid, PID, c_low, v_low, v_up, c_up]; next_eid=next_eid+1;
        end
    end
end
% Encima del top
if nabove >= 2 && ~isempty(proj_top_ids)
    for ii = 1:(nabove-1)
        v_low  = vl_above(ii);     v_up  = vl_above(ii+1);
        c_low  = proj_top_ids(ii, 1); c_up  = proj_top_ids(ii+1, 1);
        if all([v_low,v_up,c_low,c_up] > 0)
            elems(end+1,:) = [next_eid, PID, v_low, c_low, c_up, v_up]; next_eid=next_eid+1;
        end
        c_low  = proj_top_ids(ii, end); c_up  = proj_top_ids(ii+1, end);
        v_low  = vr_above(ii);          v_up  = vr_above(ii+1);
        if all([c_low,c_up,v_low,v_up] > 0)
            elems(end+1,:) = [next_eid, PID, c_low, v_low, v_up, c_up]; next_eid=next_eid+1;
        end
    end
end

%% === TIRA HORIZONTAL: entre frontera inferior (85000+/xb_bot) y 1ª fila proyectada (100000+) ===
bot_ids   = 85000 + (Nvert : Nvert+Nbot-1);
vL_bdr_id = 85000;
vR_bdr_id = 85000 + (Nvert + Nbot + Ntop);
have_proj_first_row = (nbelow>=1) && ~isempty(proj_bot_ids);
if have_proj_first_row
    top_row = proj_bot_ids(1,:);
    if vl_below(1) > 0
        n1 = bot_ids(1); n2 = vL_bdr_id; n3 = vl_below(1); n4 = top_row(1);
        elems(end+1,:) = [next_eid, PID, n1, n2, n3, n4]; next_eid=next_eid+1;
    end
    for k = 1:(Nbot-1)
        elems(end+1,:) = [next_eid, PID, bot_ids(k), bot_ids(k+1), top_row(k+1), top_row(k)]; next_eid=next_eid+1;
    end
    if vr_below(1) > 0
        n1 = vR_bdr_id; n2 = bot_ids(end); n3 = top_row(end); n4 = vr_below(1);
        elems(end+1,:) = [next_eid, PID, n1, n2, n3, n4]; next_eid=next_eid+1;
    end
end

%% === TIRA HORIZONTAL: por encima de la frontera superior (85000+/xt_top) ===
top_ids  = 85000 + (Nvert + Nbot : Nvert + Nbot + Ntop -1);
vL_top_id = 85000 + (Nvert - 1);
vR_top_id = (85000 + (Nvert + Nbot + Ntop)) + (Nvert - 1);
have_proj_first_row_top = (nabove>=1) && ~isempty(proj_top_ids);
if have_proj_first_row_top
    row_up = proj_top_ids(1,:);
    if vl_above(1) > 0
        n1 = vL_top_id; n2 = top_ids(1); n3 = row_up(1); n4 = vl_above(1);
        elems(end+1,:) = [next_eid, PID, n1, n2, n3, n4]; next_eid=next_eid+1;
    end
    for k = 1:(Ntop-1)
        elems(end+1,:) = [next_eid, PID, top_ids(k), top_ids(k+1), row_up(k+1), row_up(k)]; next_eid=next_eid+1;
    end
    if vr_above(1) > 0
        n1 = top_ids(end); n2 = vR_top_id; n3 = vr_above(1); n4 = row_up(end);
        elems(end+1,:) = [next_eid, PID, n1, n2, n3, n4]; next_eid=next_eid+1;
    end
end

%% === COLUMNAS INFERIORES con NODOS NORMALES (entre vertical y columna normal más cercana) ===
if nbelow >= 2
    j_left  = find(xg < xvL_conn, 1, 'last');
    j_right = find(xg > xvR_conn, 1, 'first');
    if ~isempty(j_left)
        for ii = 1:(nbelow-1)
            rr_low = rows_below(ii+1); rr_up = rows_below(ii);
            nL_low = rowID(rr_low, j_left); nL_up = rowID(rr_up, j_left);
            v_low  = vl_below(ii+1);        v_up  = vl_below(ii);
            if all(~isnan([nL_low nL_up])) && all([v_low v_up] > 0)
                elems(end+1,:) = [next_eid, PID, nL_low, v_low, v_up, nL_up]; next_eid=next_eid+1;
            end
        end
    end
    if ~isempty(j_right)
        for ii = 1:(nbelow-1)
            rr_low = rows_below(ii+1); rr_up = rows_below(ii);
            nR_low = rowID(rr_low, j_right); nR_up = rowID(rr_up, j_right);
            v_low  = vr_below(ii+1);         v_up  = vr_below(ii);
            if all(~isnan([nR_low nR_up])) && all([v_low v_up] > 0)
                elems(end+1,:) = [next_eid, PID, v_low, nR_low, nR_up, v_up]; next_eid=next_eid+1;
            end
        end
    end
end

%% === COLUMNAS SUPERIORES con NODOS NORMALES (entre vertical y columna normal más cercana) ===
if nabove >= 2
    j_left  = find(xg < xvL_conn, 1, 'last');
    j_right = find(xg > xvR_conn, 1, 'first');
    if ~isempty(j_left)
        for ii = 1:(nabove-1)
            rr_low = rows_above(ii);     rr_up = rows_above(ii+1);
            nL_low = rowID(rr_low, j_left); nL_up = rowID(rr_up, j_left);
            v_low  = vl_above(ii);          v_up  = vl_above(ii+1);
            if all(~isnan([nL_low nL_up])) && all([v_low v_up] > 0)
                elems(end+1,:) = [next_eid, PID, nL_low, v_low, v_up, nL_up]; next_eid=next_eid+1;
            end
        end
    end
    if ~isempty(j_right)
        for ii = 1:(nabove-1)
            rr_low = rows_above(ii);     rr_up = rows_above(ii+1);
            nR_low = rowID(rr_low, j_right); nR_up = rowID(rr_up, j_right);
            v_low  = vr_above(ii);          v_up  = vr_above(ii+1);
            if all(~isnan([nR_low nR_up])) && all([v_low v_up] > 0)
                elems(end+1,:) = [next_eid, PID, v_low, nR_low, nR_up, v_up]; next_eid=next_eid+1;
            end
        end
    end
end
% === FIN COLUMNAS SUPERIORES ===

%% === ESQUINAS: 4 elementos (micro-parche) ===
if have_proj_first_row_top || have_proj_first_row
    j_left  = find(xg < xvL_conn, 1, 'last');
    j_right = find(xg > xvR_conn, 1, 'first');

    % Arriba
    if have_proj_first_row_top && ~isempty(r_top) && ~isempty(j_left) && ~isempty(j_right)
        rr_up1 = rows_above(1);                 
        nL_top_norm = rowID(r_top, j_left);     
        nR_top_norm = rowID(r_top, j_right);    
        nL_up_norm  = rowID(rr_up1, j_left);    
        nR_up_norm  = rowID(rr_up1, j_right);   
        vL_top      = 85000 + (Nvert - 1);
        vR_top      = (85000 + (Nvert + Nbot + Ntop)) + (Nvert - 1);
        pL_top      = vl_above(1);              
        pR_top      = vr_above(1);              

        if all(~isnan([nL_top_norm nL_up_norm])) && all([vL_top pL_top] > 0)
            elems(end+1,:) = [next_eid, PID, nL_top_norm, vL_top, pL_top, nL_up_norm]; next_eid=next_eid+1;
        end
        if all(~isnan([nR_top_norm nR_up_norm])) && all([vR_top pR_top] > 0)
            elems(end+1,:) = [next_eid, PID, nR_top_norm, vR_top, pR_top, nR_up_norm]; next_eid=next_eid+1;
        end
    end

    % Abajo
    if have_proj_first_row && ~isempty(r_bottom) && ~isempty(j_left) && ~isempty(j_right)
        rr_dn1 = rows_below(1);                 
        nL_bot_norm = rowID(r_bottom, j_left);  
        nR_bot_norm = rowID(r_bottom, j_right); 
        nL_dn_norm  = rowID(rr_dn1, j_left);    
        nR_dn_norm  = rowID(rr_dn1, j_right);   
        vL_bot      = 85000;
        vR_bot      = 85000 + (Nvert + Nbot + Ntop);
        pL_bot      = vl_below(1);              
        pR_bot      = vr_below(1);              

        if all(~isnan([nL_bot_norm nL_dn_norm])) && all([vL_bot pL_bot] > 0)
            elems(end+1,:) = [next_eid, PID, nL_bot_norm, vL_bot, pL_bot, nL_dn_norm]; next_eid=next_eid+1;
        end
        if all(~isnan([nR_bot_norm nR_dn_norm])) && all([vR_bot pR_bot] > 0)
            elems(end+1,:) = [next_eid, PID, nR_bot_norm, vR_bot, pR_bot, nR_dn_norm]; next_eid=next_eid+1;
        end
    end
end
% === FIN ESQUINAS ===

%% === TIRA VERTICAL ADYACENTE A CADA LÍNEA DE SEPARACIÓN (izq y dcha) ===
getYbdr = @(id) nodes_bdr(find(nodes_bdr(:,1)==id,1,'first'), 3);
j_left  = find(xg < xvL_conn, 1, 'last');
j_right = find(xg > xvR_conn, 1, 'first');

% Vertical izquierda
Nvert = 8; % (reafirmamos)
vL_ids = 85000 + (0:(Nvert-1));
pairsL = [0 2; 2 5; 5 7];
for pp = 1:size(pairsL,1)
    id1 = vL_ids(pairsL(pp,1)+1);
    id2 = vL_ids(pairsL(pp,2)+1);
    if ~isempty(j_left) && any(nodes_bdr(:,1)==id1) && any(nodes_bdr(:,1)==id2)
        y1 = getYbdr(id1); y2 = getYbdr(id2);
        n1 = nearest_normal_by_column(j_left, y1, rowID, rows);
        n4 = nearest_normal_by_column(j_left, y2, rowID, rows);
        if all(~isnan([n1 n4])) && all([id1 id2] > 0)
            elems(end+1,:) = [next_eid, PID, n1, id1, id2, n4]; next_eid = next_eid + 1;
        end
    end
end

% Vertical derecha
vR_base = 85000 + (Nvert + Nbot + Ntop);
vR_ids  = vR_base + (0:(Nvert-1));
pairsR  = [0 2; 2 5; 5 7];
for pp = 1:size(pairsR,1)
    id1 = vR_ids(pairsR(pp,1)+1);
    id2 = vR_ids(pairsR(pp,2)+1);
    if ~isempty(j_right) && any(nodes_bdr(:,1)==id1) && any(nodes_bdr(:,1)==id2)
        y1 = getYbdr(id1); y2 = getYbdr(id2);
        n1 = nearest_normal_by_column(j_right, y1, rowID, rows);
        n4 = nearest_normal_by_column(j_right, y2, rowID, rows);
        if all(~isnan([n1 n4])) && all([id1 id2] > 0)
            elems(end+1,:) = [next_eid, PID, id1, n1, n4, id2]; next_eid = next_eid + 1;
        end
    end
end
% === FIN TIRA VERTICAL ===

%% === INSERTAR ELEMENTOS BÉZIER (PID = 1, hardcoded) ===
% (Se mantiene tu bloque tal cual)
bezier_quads = [
   99006   99008   99047   99046
   99008   99009   99048   99047
   99005   99006   99046   99045
   99003   99005   99045   99044
   99009   99011   99049   99048
   85012   99003   99044   99042
   99011   99013   99051   99049
   85011   85012   99042   99040
   85010   85011   99040   99103
   85009   85010   99103   99102
   85008   85009   99102   99101
   85000   85008   99101   85002
   99013   99014   99053   99051
   99014   99015   99055   99053
   99015   85034   99056   99055
   85033   99058   99056   85034
   85032   99104   99058   85033
   85005   99104   85032   85007
   85005   99090   99091   99104
   85002   99101   99091   99090
   99058   99104   99091   99092
   99040   99093   99092   99103
   99056   99058   99092   99093
   99028   99067   99068   99029
   99029   99068   99069   99030
   99026   99066   99067   99028
   99025   99065   99066   99026
   99023   99064   99065   99025
   85027   99063   99064   99023
   85027   85028   99061   99063
   85028   85029   99109   99061
   85029   85030   99108   99109
   85030   85031   99107   99108
   85031   85056   85058   99107
   99034   99073   99075   99035
   99033   99072   99073   99034
   99033   99032   99070   99072
   99032   99030   99069   99070
   85055   99110   85061   85063
   85054   99078   99110   85055
   85053   99076   99078   85054
   85053   99035   99075   99076
   85058   99099   99098   99107
   85061   99110   99098   99099
   99097   99109   99108   99098
   99076   99097   99098   99078
   99061   99109   99097   99096
   99075   99096   99097   99076
   99061   99096   99095   99063
   99073   99095   99096   99075
   99091   99102   99103   99092
   99040   99042   99094   99093
   99055   99056   99093   99094
];
bezier_trias = [
   99094   99053   99055
   85002   99090   85005
   99053   99094   99051
   99049   99051   99094
   99042   99044   99094
   99044   99045   99094
   99045   99046   99094
   99046   99047   99094
   99047   99048   99094
   99048   99049   99094
   85058   85061   99099
   99078   99098   99110
   99098   99108   99107
   99073   99072   99095
   99070   99095   99072
   99064   99063   99095
   99064   99095   99065
   99065   99095   99066
   99066   99095   99067
   99067   99095   99068
   99069   99095   99070
   99068   99095   99069
   99091   99101   99102
];
all_nodes_ids = [nodes_ext(:,1); nodes_bdr(:,1); nodes_int(:,1); nodes_proj(:,1)];
warn_missing = @(ids) any(~ismember(ids, all_nodes_ids));
for r = 1:size(bezier_quads,1)
    n = bezier_quads(r,:);
    if warn_missing(n)
        fprintf('WARN Bézier CQUAD4 omitido por nodos inexistentes: [%d %d %d %d]\n', n(1),n(2),n(3),n(4));
        continue;
    end
    elems(end+1,:) = [next_eid, PID, n(1), n(2), n(3), n(4)]; next_eid = next_eid + 1;
end
for r = 1:size(bezier_trias,1)
    n = bezier_trias(r,:);
    if warn_missing(n)
        fprintf('WARN Bézier CTRIA3 omitido por nodos inexistentes: [%d %d %d]\n', n(1),n(2),n(3));
        continue;
    end
    elems_tri(end+1,:) = [next_eid, PID, n(1), n(2), n(3)]; next_eid = next_eid + 1;
end

%% === INSERTAR ELEMENTOS GAP (RESINA) — PID=2 ===
gap_quads = [  
   85037 99013 99011 85038
   85038 99011 99009 85039
   85017 85018 85042 85041
   85018 85019 85043 85042
   85019 85020 85044 85043
   85020 85021 85045 85044
   85021 85022 85046 85045
   85013 85014 99005 99003
   85014 85015 99006 99005
   85025 85026 99023 99025
   85024 85025 99025 99026
   85050 85049 99032 99033
   85048 99030 99032 85049
];
gap_trias = [
   99015 99014 85035
   99014 85036 85035
   99014 99013 85036
   99013 85037 85036
   99034 99035 85052
   85051 99034 85052
   99033 99034 85051
   85050 99033 85051
   85034 99015 85035
   85012 85013 99003
   85039 99009 99008
   85015 99008 99006
   85026 85027 99023
   85052 99035 85053
   85024 99026 99028
   85048 99029 99030
   85048 99028 99029
   85039 99008 85040
   85015 85016 99008
   85047 99028 85048
   85023 85024 99028
   85040 99008 85041
   85016 85017 99008
   85017 85041 99008
   85046 99028 85047
   85022 85023 99028
   85022 99028 85046
];
for r = 1:size(gap_quads,1)
    n = gap_quads(r,:);
    if warn_missing(n)
        fprintf('WARN GAP CQUAD4 omitido por nodos inexistentes: [%d %d %d %d]\n', n(1),n(2),n(3),n(4));
        continue;
    end
    elems(end+1,:) = [next_eid, 2, n(1), n(2), n(3), n(4)]; next_eid = next_eid + 1;
end
for r = 1:size(gap_trias,1)
    n = gap_trias(r,:);
    if warn_missing(n)
        fprintf('WARN GAP CTRIA3 omitido por nodos inexistentes: [%d %d %d]\n', n(1),n(2),n(3));
        continue;
    end
    elems_tri(end+1,:) = [next_eid, 2, n(1), n(2), n(3)]; next_eid = next_eid + 1;
end

%% ================== PODA: eliminar nodos_ext en [xvL,xvR] y sus elementos ==================
if ~isnan(xvL_conn) && ~isnan(xvR_conn)
    x_min_gap = min(xvL_conn, xvR_conn);
    x_max_gap = max(xvL_conn, xvR_conn);

    if ~isempty(nodes_ext)
        mask_ext_keep = ~(nodes_ext(:,2) >= x_min_gap & nodes_ext(:,2) <= x_max_gap);
        bad_ids = nodes_ext(~mask_ext_keep, 1);
        nodes_ext = nodes_ext(mask_ext_keep, :);
    else
        bad_ids = [];
    end

    if ~isempty(bad_ids) && ~isempty(elems)
        conn = elems(:,3:end); 
        to_kill = any(ismember(conn, bad_ids), 2);
        elems = elems(~to_kill, :);
    end
    if ~isempty(bad_ids) && ~isempty(elems_tri)
        connT = elems_tri(:,3:end);
        to_killT = any(ismember(connT, bad_ids), 2);
        elems_tri = elems_tri(~to_killT, :);
    end
end

%% ========== ASIGNACIÓN DE COMPONENTES (debajo y ENCIMA del GAP) ==========
% Debajo: bandas horizontales (como ya tenías)
y_gap_bottom = y_ifc(ply_gap);
epsY = 1e-9;

% --- Funciones centroides:
get_yc_quad = @(n1,n2,n3,n4) mean([ ...
    get_xy_by_id(n1, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ...
   ;get_xy_by_id(n2, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ...
   ;get_xy_by_id(n3, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ...
   ;get_xy_by_id(n4, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ], 1);
get_yc_tri  = @(n1,n2,n3) mean([ ...
    get_xy_by_id(n1, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ...
   ;get_xy_by_id(n2, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ...
   ;get_xy_by_id(n3, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ], 1);

% ---------- QUADs: asignación inferior ----------
for iQ = 1:size(elems,1)
    pid = elems(iQ,2);
    if pid==2, continue; end % resina
    n1=elems(iQ,3); n2=elems(iQ,4); n3=elems(iQ,5); n4=elems(iQ,6);
    [ok1,~,y1]=get_xy_by_id(n1, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    [ok2,~,y2]=get_xy_by_id(n2, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    [ok3,~,y3]=get_xy_by_id(n3, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    [ok4,~,y4]=get_xy_by_id(n4, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    if ~(ok1&&ok2&&ok3&&ok4), continue; end
    yc = mean([y1 y2 y3 y4]);

    % Debajo del gap (igual que antes)
    if yc < y_gap_bottom - epsY
        kband = floor((yc + epsY)/t_ply) + 1;  % 1..ply_gap-1
        kband = max(1, min(kband, ply_gap-1));
        elems(iQ,2) = 100 + kband;
        continue;
    end

    % ENCIMA del gap: clasificar por lámina ondulada usando Yg(i,:)—Yg(i+1,:)
    % ENCIMA del gap: primero clasificar LA LÁMINA DEL GAP y luego las superiores
if yc >= y_gap_bottom - epsY
    xc = mean([ ...
        nodes_coord_x(n1, nodes_ext, nodes_bdr, nodes_int, nodes_proj), ...
        nodes_coord_x(n2, nodes_ext, nodes_bdr, nodes_int, nodes_proj), ...
        nodes_coord_x(n3, nodes_ext, nodes_bdr, nodes_int, nodes_proj), ...
        nodes_coord_x(n4, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ]);

    % --- rango vertical de la lámina del GAP en x = xc
    ylow_pg = y_ifc(ply_gap);
    yup_pg  = interp1(xg, Yg(ply_gap+1,:), xc, 'linear','extrap');

    % Si el centroide cae dentro de la lámina del GAP -> PID 100+ply_gap
    if yc >= (min(ylow_pg, yup_pg) - 1e-9) && yc <= (max(ylow_pg, yup_pg) + 1e-9)
        elems(iQ,2) = 100 + ply_gap;
        continue;  % ¡no seguir buscando!
    end

    % --- resto de láminas superiores (ply_gap+1..N)
    for i = (ply_gap+1):N
        ylow = interp1(xg, Yg(i,:),   xc, 'linear','extrap');
        yup  = interp1(xg, Yg(i+1,:), xc, 'linear','extrap');
        ylo = min(ylow,yup) - 1e-9; 
        yhi = max(ylow,yup) + 1e-9;
        if (yc >= ylo) && (yc <= yhi)
            elems(iQ,2) = 200 + (i - ply_gap); % 201.. para láminas superiores
            break;
        end
    end
end

    
end

% ---------- TRIA3: asignación inferior/superior ----------
for iT = 1:size(elems_tri,1)
    pid = elems_tri(iT,2);
    if pid==2, continue; end % resina
    n1=elems_tri(iT,3); n2=elems_tri(iT,4); n3=elems_tri(iT,5);
    [ok1,~,y1]=get_xy_by_id(n1, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    [ok2,~,y2]=get_xy_by_id(n2, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    [ok3,~,y3]=get_xy_by_id(n3, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    if ~(ok1&&ok2&&ok3), continue; end
    yc = mean([y1 y2 y3]);

    if yc < y_gap_bottom - epsY
        kband = floor((yc + epsY)/t_ply) + 1;
        kband = max(1, min(kband, ply_gap-1));
        elems_tri(iT,2) = 100 + kband;
        continue;
    end

    if yc >= y_gap_bottom - epsY
    xc = mean([ ...
        nodes_coord_x(n1, nodes_ext, nodes_bdr, nodes_int, nodes_proj), ...
        nodes_coord_x(n2, nodes_ext, nodes_bdr, nodes_int, nodes_proj), ...
        nodes_coord_x(n3, nodes_ext, nodes_bdr, nodes_int, nodes_proj) ]);

    % --- rango vertical de la lámina del GAP en x = xc
    ylow_pg = y_ifc(ply_gap);
    yup_pg  = interp1(xg, Yg(ply_gap+1,:), xc, 'linear','extrap');

    % Si el centroide cae dentro de la lámina del GAP -> PID 100+ply_gap
    if yc >= (min(ylow_pg, yup_pg) - 1e-9) && yc <= (max(ylow_pg, yup_pg) + 1e-9)
        elems_tri(iT,2) = 100 + ply_gap;
        continue;
    end

    % --- resto de láminas superiores
    for i = (ply_gap+1):N
        ylow = interp1(xg, Yg(i,:),   xc, 'linear','extrap');
        yup  = interp1(xg, Yg(i+1,:), xc, 'linear','extrap');
        ylo = min(ylow,yup) - 1e-9; 
        yhi = max(ylow,yup) + 1e-9;
        if (yc >= ylo) && (yc <= yhi)
            elems_tri(iT,2) = 200 + (i - ply_gap);
            break;
        end
    end
end

    
end
%% ========= FIN ASIGNACIÓN DE COMPONENTES =========

fprintf(['Nodos exteriores (tras poda): %d | Nodos frontera GAP (85000+): %d | ', ...
         'Nodos GAP internos (99000+): %d | Nodos PROYECTADOS (100000+): %d | CQUAD4: %d | CTRIA3: %d | ELEMS totales: %d\n'], ...
    size(nodes_ext,1), size(nodes_bdr,1), size(nodes_int,1), size(nodes_proj,1), size(elems,1), size(elems_tri,1), size(elems,1)+size(elems_tri,1));

%% === PARCHE FINAL: Orientar todas las normales a +Z ===
[elems, elems_tri, flipsQ, flipsT, skippedQ, skippedT] = enforce_normals_plusZ( ...
    elems, elems_tri, nodes_ext, nodes_bdr, nodes_int, nodes_proj);

fprintf('--- Corrección de normales a +Z ---\n');
fprintf('CQUAD4 invertidos: %d (saltados: %d)\n', flipsQ, skippedQ);
fprintf('CTRIA3  invertidos: %d (saltados: %d)\n', flipsT, skippedT);

% ---- Exportar BDF ----
outfile = 'laminado_gap_mesh.bdf';
nodes_all = [nodes_ext; nodes_bdr; nodes_int; nodes_proj];  % guardo para el post-proceso
write_bdf(outfile, nodes_all, elems, elems_tri, t_ply, ply_gap, N, Yg, xg, theta_vec,W);
fprintf('Archivo BDF escrito: %s\n', outfile);



%% ====================== FUNCIONES (deben ir al final) ======================
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
% Comprueba que la curva Bézier (xb,yb) queda entre las superficies
% inferior y superior con un margen >= -tol en todo el tramo [gapLR(1), gapLR(2)].

    % Limitar xb al intervalo del gap
    xb = min(max(xb, gapLR(1)), gapLR(2));

    % Interpolar las superficies en los puntos xb
    y_low = interp1(xgrid, y_low_vec, xb, 'linear', 'extrap');
    y_up  = interp1(xgrid, y_up_vec,  xb, 'linear', 'extrap');

    % Distancias a cada superficie
    d_low = yb - y_low;   % debe ser >= -tol
    d_up  = y_up - yb;    % debe ser >= -tol

    % Mínimos a reportar
    min_low = min(d_low);
    min_up  = min(d_up);

    % OK si respeta la holgura por ambos lados
    ok = (min_low >= -abs(tol)) && (min_up >= -abs(tol));
end



function xhit = get_x_at_y_on_curve(xc, yc, yq, mode)
    xhit = NaN; xs=[];
    for k=1:numel(yc)-1
        y1=yc(k); y2=yc(k+1);
        if (y1 - yq)*(y2 - yq) <= 0
            if y2~=y1
                t=(yq - y1)/(y2 - y1);
                xs(end+1)=xc(k) + t*(xc(k+1)-xc(k));
            else
                xs(end+1)=xc(k); xs(end+1)=xc(k+1);
            end
        end
    end
    if isempty(xs), return; end
    if strcmpi(mode,'max'), xhit=max(xs); else, xhit=min(xs); end
end

function nid = nearest_normal_by_column(jcol, y_target, rowID, rows)
% Devuelve el ID del nodo normal en la columna jcol cuya coordenada Y
% es la más cercana a y_target. Si no hay candidato, devuelve NaN.
    best = NaN; best_d = inf;
    for r = 1:numel(rows)
        nid_r = rowID(r, jcol);
        if ~isnan(nid_r)
            y_r = rows(r).y(jcol);
            d = abs(y_r - y_target);
            if d < best_d
                best_d = d; best = nid_r;
            end
        end
    end
    nid = best;
end

function x = nodes_coord_x(id, nodes_ext, nodes_bdr, nodes_int, nodes_proj)
% Devuelve la coordenada X del nodo 'id'. Si no existe, NaN.
    [ok, x, ~] = get_xy_by_id(id, nodes_ext, nodes_bdr, nodes_int, nodes_proj);
    if ~ok
        x = NaN;
    end
end

%% ========= Helpers de orientación (parche +Z) =========
function [elemsQ, elemsT, flipsQ, flipsT, skippedQ, skippedT] = enforce_normals_plusZ(elemsQ, elemsT, nodes_ext, nodes_bdr, nodes_int, nodes_proj)
% Asegura que todas las normales apunten a +Z invirtiendo conectividades si hace falta.
% Quads: swap n2 <-> n4 ; Trias: swap n2 <-> n3
    flipsQ = 0; flipsT = 0; skippedQ = 0; skippedT = 0;

    % ---- Quads
    for i = 1:size(elemsQ,1)
        n = elemsQ(i,3:6);
        [ok1,x1,y1] = get_xy_by_id(n(1), nodes_ext, nodes_bdr, nodes_int, nodes_proj);
        [ok2,x2,y2] = get_xy_by_id(n(2), nodes_ext, nodes_bdr, nodes_int, nodes_proj);
        [ok3,x3,y3] = get_xy_by_id(n(3), nodes_ext, nodes_bdr, nodes_int, nodes_proj);
        [ok4,x4,y4] = get_xy_by_id(n(4), nodes_ext, nodes_bdr, nodes_int, nodes_proj);
        if ~(ok1&&ok2&&ok3&&ok4)
            skippedQ = skippedQ + 1; 
            continue;
        end
        A = poly_area_signed([x1 x2 x3 x4],[y1 y2 y3 y4]); % CCW > 0 => +Z
        if A < 0
            elemsQ(i,[4 6]) = elemsQ(i,[6 4]); % swap n2<->n4 (col 4 y 6 en registro)
            flipsQ = flipsQ + 1;
        end
    end

    % ---- Trias
    for i = 1:size(elemsT,1)
        n = elemsT(i,3:5);
        [ok1,x1,y1] = get_xy_by_id(n(1), nodes_ext, nodes_bdr, nodes_int, nodes_proj);
        [ok2,x2,y2] = get_xy_by_id(n(2), nodes_ext, nodes_bdr, nodes_int, nodes_proj);
        [ok3,x3,y3] = get_xy_by_id(n(3), nodes_ext, nodes_bdr, nodes_int, nodes_proj);
        if ~(ok1&&ok2&&ok3)
            skippedT = skippedT + 1;
            continue;
        end
        A = poly_area_signed([x1 x2 x3],[y1 y2 y3]); % CCW > 0 => +Z
        if A < 0
            elemsT(i,[4 5]) = elemsT(i,[5 4]); % swap n2<->n3 (col 4 y 5)
            flipsT = flipsT + 1;
        end
    end
end

function [ok,x,y] = get_xy_by_id(id, nodes_ext, nodes_bdr, nodes_int, nodes_proj)
% Busca coordenadas XY por ID en cualquiera de los bancos de nodos.
    x = NaN; y = NaN; ok = false;
    if ~isempty(nodes_ext)
        idx = find(nodes_ext(:,1)==id,1,'first');
        if ~isempty(idx), x = nodes_ext(idx,2); y = nodes_ext(idx,3); ok = true; return; end
    end
    if ~isempty(nodes_bdr)
        idx = find(nodes_bdr(:,1)==id,1,'first');
        if ~isempty(idx), x = nodes_bdr(idx,2); y = nodes_bdr(idx,3); ok = true; return; end
    end
    if ~isempty(nodes_int)
        idx = find(nodes_int(:,1)==id,1,'first');
        if ~isempty(idx), x = nodes_int(idx,2); y = nodes_int(idx,3); ok = true; return; end
    end
    if ~isempty(nodes_proj)
        idx = find(nodes_proj(:,1)==id,1,'first');
        if ~isempty(idx), x = nodes_proj(idx,2); y = nodes_proj(idx,3); ok = true; return; end
    end
end

function A = poly_area_signed(xv,yv)
% Área firmada de un polígono en XY.
% CCW -> A>0 (normal +Z),  CW -> A<0 (normal -Z).
    x2 = [xv(2:end) xv(1)]; y2 = [yv(2:end) yv(1)];
    A = 0.5 * sum(xv.*y2 - x2.*yv);
end

function [theta_vec, layup_label] = ask_apilado_pack()
% Devuelve theta_vec (lista de ángulos, en grados) y una etiqueta.
% Todas las opciones son SIMÉTRICAS y EQUILIBRADAS (se espeja el semipack con 's').

    fprintf('\n=== Selección de apilado (packs típicos, simétricos y equilibrados) ===\n');
    fprintf(' 1) QI-8   : [45/0/-45/90]s\n');
    fprintf(' 2) QI-16  : [45/0/-45/90/0/-45/0/45]s\n');
    fprintf(' 3) ±45 sesgado (14): [45/0/-45/90/45/0/-45]s\n');
    fprintf(' 4) 0° dominante (14): [0/45/-45/0/90/0/45]s\n');
    fprintf(' 5) 90° reforzado (16): [45/0/90/0/-45/0/90/0]\n');
    fprintf(' 6) Spread-tow (16): [45/0/-45/90/-45/0/45/90]\n');

    choice = [];
    while isempty(choice) || ~isscalar(choice) || ~ismember(choice,1:6)
        choice = input('Selecciona pack (1-6): ');
        if isempty(choice) || ~isscalar(choice) || ~ismember(choice,1:6)
            fprintf('  >> Opción inválida. Prueba 1..6.\n');
        end
    end

    switch choice
        case 1  % QI-8
            base = [45, 0, -45, 90];
            layup_label = '[45/0/-45/90]s (QI-8)';
        case 2  % QI-16 reforzado en 0°
            base = [45, 0, -45, 90, 0, -45, 0, 45];
            layup_label = '[45/0/-45/90/0/-45/0/45]s (QI-16)';
        case 3  % ±45 sesgado (14)
            base = [45, 0, -45, 90, 45, 0, -45];
            layup_label = '[45/0/-45/90/45/0/-45]s (±45 sesgado, 14)';
        case 4  % 0° dominante (14)
            base = [0, 45, -45, 0, 90, 0, 45];
            layup_label = '[0/45/-45/0/90/0/45]s (0° dominante, 14)';
        case 5  % 90° reforzado (16)
            base = [45, 0, 90, 0, -45, 0, 90, 0];
            layup_label = '[45/0/90/0/-45/0/90/0]s (90° reforzado, 16)';
        case 6  % Spread-tow fino repetitivo (16)
            base = [45, 0, -45, 90, -45, 0, 45, 90];
            layup_label = '[45/0/-45/90/-45/0/45/90]s (Spread-tow, 16)';
    end

    % Expandir a simétrico: semipack + espejo (palíndromo)
    theta_vec = [base, fliplr(base)];

    % Guardrail: mínimo 5 láminas
    if numel(theta_vec) < 5
        error('El apilado debe tener al menos 5 láminas (este tiene %d).', numel(theta_vec));
    end
end

function write_bdf(filename, nodes_all, elems_quads, elems_trias, t_ply, ply_gap, N, Yg, xg, theta_vec, W)

    fid = fopen(filename,'w'); if fid<0, error('No se pudo abrir %s', filename); end
    fprintf(fid,'$ Generated by MATLAB - malla exterior + GAP (IDs fijos) + PROYECCION + PODA + BÉZIER\n');

    %% ====== IDs que usaremos en Case Control y en el BULK ======
    SID_SPC   = 900099;  % único set de SPC
    SID_SPCD  = 900040;  % set para SPCD (UX borde derecho)

    %% ====== CASE CONTROL / LOAD STEP (antes de BEGIN BULK) ======

    fprintf(fid,'$HMNAME LOADSTEP %d "loadstep1"\n', 1);
    fprintf(fid,'\n');
    fprintf(fid,'SUBCASE 1\n');
    fprintf(fid,'   LABEL loadstep1\n');
    fprintf(fid,'   ANALYSIS STATICS\n');
    fprintf(fid,'   SPC   = %d\n', SID_SPC);
    fprintf(fid,'   LOAD  = %d\n', SID_SPCD);
    fprintf(fid,'   DISPLACEMENT = ALL\n');
    fprintf(fid,'   STRESS = YES\n');
    fprintf(fid,'   SPCF = ALL\n');
    fprintf(fid,'\n');

    %% ====== COMIENZO DEL BULK ======
    fprintf(fid,'BEGIN BULK\n');

    %% ----------------------- MATERIALES -----------------------
    fprintf(fid,'MAT1,1,%.9g,,%.9g\n', 4660, 0.35);
    fprintf(fid,'$HMNAME MAT 1 "RESIN_8552_2D"\n');

    fprintf(fid,'$ === UD 8552/AS4 (RTD, seco) | MAT8 por orientación ===\n');
    fprintf(fid,'MAT8,1001,127300,9240,0.302,4830,4830,3600,1.600000000e-09\n');
    fprintf(fid,'+ , , , , , , , ,1996,1398,63.9,268,74\n');
    fprintf(fid,'$HMNAME MAT 1001 "UD_8552_AS4_0deg"\n');

    fprintf(fid,'MAT8,1002,12563.8,12563.8,0.3006,6100.1,4830,3600,1.600000000e-09\n');
    fprintf(fid,'+ , , , , , , , ,1996,1398,63.9,268,74\n');
    fprintf(fid,'$HMNAME MAT 1002 "UD_8552_AS4_+45deg"\n');

    fprintf(fid,'MAT8,1003,12563.8,12563.8,0.3006,6100.1,4830,3600,1.600000000e-09\n');
    fprintf(fid,'+ , , , , , , , ,1996,1398,63.9,268,74\n');
    fprintf(fid,'$HMNAME MAT 1003 "UD_8552_AS4_-45deg"\n');

    fprintf(fid,'MAT8,1004,9240,127300,0.0219205,4830,4830,3600,1.600000000e-09\n');
    fprintf(fid,'+ , , , , , , , ,1996,1398,63.9,268,74\n');
    fprintf(fid,'$HMNAME MAT 1004 "UD_8552_AS4_90deg"\n');

    %% ----------------------- PROPIEDADES (sin plane strain) -----------------------
    tp = t_ply/3; % 3 tiras por lámina

    fprintf(fid,'PSHELL,2,1,%.6f\n', tp);   % Resina GAP (sin MID2=-1)
    fprintf(fid,'$HMNAME PROP 2 "GAP_RESIN_2D"\n');

    mat_id_for = @(th) local_mid_for(th);

    % Serie 100
    for i = 1:ply_gap
        mid = mat_id_for(theta_vec(i)); pid = 100 + i;
        fprintf(fid,'PSHELL,%d,%d,%.6f\n', pid, mid, tp);
        fprintf(fid,'$HMNAME PROP %d "PLY_%02d_2D"\n', pid, i);
    end
    % Serie 200
    for i = (ply_gap+1):N
        mid = mat_id_for(theta_vec(i)); pid = 200 + (i - ply_gap);
        fprintf(fid,'PSHELL,%d,%d,%.6f\n', pid, mid, tp);
        fprintf(fid,'$HMNAME PROP %d "PLY_%02d_2D"\n', pid, i);
    end

    %% ----------------------- NODOS -----------------------
    for i=1:size(nodes_all,1)
        fprintf(fid,'GRID,%d,0,%.6f,%.6f,%.6f\n', nodes_all(i,1), nodes_all(i,2), nodes_all(i,3), nodes_all(i,4));
    end

    %% ----------------------- SETS para HM (visual) -----------------------
    SET_ALL   = 900100;
    SET_LEFT  = 900101;
    SET_REF   = 900102; % nodo de ref (esquina inf. izq.)
    SET_RIGHT = 900103;

    write_hm_grid_set(fid, SET_ALL,  'ALL_NODES',  nodes_all(:,1).');

    x_all = nodes_all(:,2); xmin = min(x_all); xmax = max(x_all);
    tolx  = max(1e-8, 1e-6*(xmax-xmin));

    left_ids  = unique(nodes_all(x_all <= xmin + tolx, 1).','stable');
    right_ids = unique(nodes_all(x_all >= xmax - tolx, 1).','stable');

    fprintf(fid,'$ Left-edge nodes detected: %d (tolx=%.3e, xmin=%.9g)\n',  numel(left_ids),  tolx, xmin);
    fprintf(fid,'$ Right-edge nodes detected: %d (tolx=%.3e, xmax=%.9g)\n', numel(right_ids), tolx, xmax);

    write_hm_grid_set(fid, SET_LEFT,  'LEFT_EDGE',  left_ids);
    write_hm_grid_set(fid, SET_RIGHT, 'RIGHT_EDGE', right_ids);

    % nodo de referencia (mín Y dentro de borde izq.)
    if ~isempty(left_ids)
        left_mask  = ismember(nodes_all(:,1), left_ids(:));
        left_table = nodes_all(left_mask, :);
        [~, iminY] = min(left_table(:,3));
        nid_ref    = left_table(iminY, 1);
        write_hm_grid_set(fid, SET_REF, 'LEFT_BOTTOM_NODE', nid_ref);
    else
        nid_ref = [];
        fprintf(fid,'$ WARN: No left_ids found to define LEFT_BOTTOM_NODE set.\n');
    end

    %% ----------------------- SPC (TODO en un único SID) -----------------------
    dUX = 0.02 * W;   % lo usamos más abajo para SPCD

    all_ids = nodes_all(:,1);

    % UZ = 0 para TODOS los nodos (comp 3)
    fprintf(fid,'$ === SPC: UZ=0 en TODOS los GRID ===\n');
    for ii = 1:numel(all_ids)
        fprintf(fid,'SPC,%d,%d,3,0.0\n', SID_SPC, all_ids(ii));
    end

    % UX = 0 para el borde IZQUIERDO (comp 1)
    fprintf(fid,'$ === SPC: UX=0 en BORDE IZQUIERDO ===\n');
    for ii = 1:numel(left_ids)
        fprintf(fid,'SPC,%d,%d,1,0.0\n', SID_SPC, left_ids(ii));
    end

    % UY = 0 en nodo de referencia (comp 2)
    if ~isempty(nid_ref)
        fprintf(fid,'$ === SPC: UY=0 en nodo de referencia (esquina inf. izq.) ===\n');
        fprintf(fid,'SPC,%d,%d,2,0.0\n', SID_SPC, nid_ref);
    else
        fprintf(fid,'$ WARN: No reference node for UY=0 SPC.\n');
    end

    % UX = 0 en BORDE DERECHO (requisito para SPCD); UZ ya está a 0 globalmente
    fprintf(fid,'$ === SPC: UX=0 en BORDE DERECHO (requisito para SPCD) ===\n');
    for ii = 1:numel(right_ids)
        fprintf(fid,'SPC,%d,%d,1,0.0\n', SID_SPC, right_ids(ii));
    end

    %% ----------------------- SPCD (desplazamiento impuesto UX) -----------------------
    fprintf(fid,'$ === SPCD: UX = %+ .9g en BORDE DERECHO ===\n', dUX);
    for ii = 1:numel(right_ids)
        fprintf(fid,'SPCD,%d,%d,1,%.9g\n', SID_SPCD, right_ids(ii), dUX);
    end

    %% ----------------------- ELEMENTOS -----------------------
    for e=1:size(elems_quads,1)
        fprintf(fid,'CQUAD4,%d,%d,%d,%d,%d,%d\n', elems_quads(e,1), elems_quads(e,2), elems_quads(e,3), elems_quads(e,4), elems_quads(e,5), elems_quads(e,6));
    end
    for e=1:size(elems_trias,1)
        fprintf(fid,'CTRIA3,%d,%d,%d,%d,%d\n', elems_trias(e,1), elems_trias(e,2), elems_trias(e,3), elems_trias(e,4), elems_trias(e,5));
    end

    fprintf(fid,'ENDDATA\n');
    fclose(fid);

    %% ===== helpers locales =====
    function mid = local_mid_for(th)
        thn = mod(th,180);
        eq = @(a,b) abs(a-b) < 1e-6;
        if     eq(thn,0),   mid = 1001;
        elseif eq(thn,45),  mid = 1002;
        elseif eq(thn,135), mid = 1003;
        elseif eq(thn,90),  mid = 1004;
        else, error('Ángulo no soportado: %.3f', th);
        end
    end

    function write_hm_grid_set(fid, set_id, set_name, ids)
        perline_loc = 8;
        fprintf(fid,'$HMSET%10d%9d "%s" 18\n', set_id, 1, set_name);
        fprintf(fid,'$HMSETTYPE%10d "non-ordered" 18\n', 1);
        fprintf(fid,'SET%9d%8s%8s\n', set_id, 'GRID', 'LIST');
        ids = ids(:).';
        k = 1;
        while k <= numel(ids)
            nthis = min(perline_loc, numel(ids)-k+1);
            fprintf(fid,'+');
            for j=0:nthis-1, fprintf(fid,'%8d', ids(k+j)); end
            fprintf(fid,'\n');
            k = k + nthis;
        end
    end
end
