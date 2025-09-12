<script lang="ts">
  export let open = false;
  export let closeOnBackdrop = true;
  export let title: string = "Dialog";

  let dialog: HTMLDialogElement;

  $: if (dialog) {
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }

  function closeModal() {
    open = false;
  }

  function clickDiolag(e: MouseEvent) {
    if (closeOnBackdrop && e.target === dialog) closeModal();
  }
</script>

<dialog
  bind:this={dialog}
  class="modal"
  on:close={closeModal}
  on:click={clickDiolag}
  aria-modal="true"
  style={`--modal-width:min(900px, 96vw)};`}
>
  <div class="panel">
    <header class="modal-header">
      <h2 class="modal-title">{title}</h2>
      <button type="button" class="icon-btn" aria-label="Close" on:click={closeModal}>✕</button>
    </header>

    <main class="modal-body">
      <slot></slot>
    </main>

    <footer class="modal-footer">
      <slot name="footer"></slot>
    </footer>
  </div>
</dialog>

<style>
  /* Reset for perfect alignment */
  :global(*), :global(*::before), :global(*::after) { box-sizing: border-box; }

  /* Backdrop */
  .modal::backdrop {
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(2px);
  }

  /* Dialog shell */
  .modal {
    background: transparent;     /* prevent white corners */
    border: none;
    padding: 0;
    margin: auto;                /* center in viewport */
    width: var(--modal-width, min(900px, 96vw)); /* single width control */
    max-width: none;
    overflow: visible;
  }
  .modal[open] {
    animation: scale-in 140ms ease-out;
  }

  /* Panel (actual visible box) */
  .panel {
    background: var(--panel, #151a21);
    color: var(--text, #eef1f4);
    border: 1px solid var(--panel-border, rgba(255,255,255,0.06));
    border-radius: 16px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.55);
    overflow: hidden; /* clean rounded corners */
  }

  /* Header / Body / Footer */
  .modal-header,
  .modal-footer {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 20px;
  }
  .modal-header {
    justify-content: space-between;
    border-bottom: 1px solid var(--panel-border, rgba(255,255,255,0.06));
  }
  .modal-body {
    padding: 20px;
  }
  .modal-footer {
    justify-content: flex-end;
    border-top: 1px solid var(--panel-border, rgba(255,255,255,0.06));
  }

  /* Title + Close */
  .modal-title {
    margin: 0;
    font-weight: 800;
    letter-spacing: -0.01em;
    font-size: 18px;
  }
  .icon-btn {
    background: transparent;
    border: 1px solid transparent;
    color: inherit;
    font-size: 18px;
    line-height: 1;
    padding: 6px 10px;
    border-radius: 10px;
    cursor: pointer;
    transition: background .15s ease, border-color .15s ease, transform .06s ease;
  }
  .icon-btn:hover {
    background: rgba(255,255,255,0.06);
    border-color: var(--panel-border, rgba(255,255,255,0.06));
  }
  .icon-btn:active { transform: translateY(1px); }

  /* Animation */
  @keyframes scale-in {
    from { transform: translateY(-4px) scale(0.985); opacity: 0; }
    to   { transform: translateY(0)    scale(1);     opacity: 1; }
  }

  /* Mobile tweaks */
  @media (max-width: 760px) {
    .modal { width: min(96vw, 680px); }
    .modal-header, .modal-footer, .modal-body { padding: 14px 16px; }
  }
</style>

