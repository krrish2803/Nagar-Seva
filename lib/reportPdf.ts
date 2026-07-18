export type PdfReportData = {
  issue_title: string
  issue_description: string
  address: string
  latitude: string
  longitude: string
  ward_id: string
  pin_code: string
  uploaded_image_name: string
  complaint_id?: string
}

function escapeHtml(value?: string | number) {
  return String(value || 'Not provided')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

export function generateIssuePdf(data: PdfReportData) {
  const title = data.issue_title || 'Civic Issue Report'
  const rows = [
    ['Complaint ID', data.complaint_id || 'Pending'],
    ['Issue Title', data.issue_title],
    ['Description', data.issue_description],
    ['Address', data.address],
    ['Latitude', data.latitude],
    ['Longitude', data.longitude],
    ['Ward', data.ward_id],
    ['PIN', data.pin_code],
    ['Uploaded Image Name', data.uploaded_image_name],
    ['Generated At', new Date().toLocaleString('en-IN')],
  ]
  const safeTitle = escapeHtml(title)
  const reportRows = rows
    .map(
      ([label, value]) => `
        <div class="row">
          <div class="label">${escapeHtml(label)}</div>
          <div class="value">${escapeHtml(value)}</div>
        </div>
      `
    )
    .join('')
  const printWindow = window.open('', '_blank', 'noopener,noreferrer,width=900,height=1100')
  const html = `
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <title>NagarSeva Issue Report - ${safeTitle}</title>
    <style>
      @page { size: A4; margin: 18mm; }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        color: #2C2C2A;
        background: #E8F5F0;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }
      .sheet {
        min-height: 100vh;
        background:
          radial-gradient(circle at 16% 0%, rgba(29, 158, 117, 0.18), transparent 260px),
          radial-gradient(circle at 92% 18%, rgba(55, 138, 221, 0.18), transparent 280px),
          #ffffff;
        border: 1px solid rgba(29, 158, 117, 0.16);
        border-radius: 28px;
        overflow: hidden;
        box-shadow: 0 24px 80px rgba(44, 44, 42, 0.16);
      }
      .hero {
        position: relative;
        padding: 36px;
        color: white;
        background: linear-gradient(135deg, #0F6E56 0%, #185FA5 62%, #EB6834 100%);
      }
      .hero::after {
        content: "";
        position: absolute;
        inset: 0;
        opacity: 0.18;
        background-image:
          linear-gradient(rgba(255,255,255,.28) 1px, transparent 1px),
          linear-gradient(90deg, rgba(255,255,255,.28) 1px, transparent 1px);
        background-size: 42px 42px;
      }
      .hero-content { position: relative; z-index: 1; }
      .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-weight: 900;
        letter-spacing: -0.02em;
      }
      .logo {
        display: inline-flex;
        width: 44px;
        height: 44px;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.28);
      }
      h1 {
        margin: 30px 0 8px;
        max-width: 720px;
        font-size: 40px;
        line-height: 1.05;
        letter-spacing: -0.05em;
      }
      .subtitle {
        margin: 0;
        max-width: 640px;
        color: rgba(255,255,255,0.82);
        font-size: 15px;
        line-height: 1.7;
      }
      .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 22px;
      }
      .badge {
        border: 1px solid rgba(255,255,255,0.24);
        border-radius: 999px;
        background: rgba(255,255,255,0.13);
        padding: 8px 12px;
        font-size: 12px;
        font-weight: 800;
      }
      .content { padding: 34px 36px 28px; }
      .section-title {
        margin: 0 0 18px;
        color: #0F6E56;
        font-size: 13px;
        font-weight: 900;
        letter-spacing: 0.18em;
        text-transform: uppercase;
      }
      .grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 14px;
      }
      .row {
        min-height: 86px;
        border: 1px solid #E5EEE9;
        border-radius: 18px;
        background: #FBFEFC;
        padding: 16px;
      }
      .row:nth-child(3) {
        grid-column: 1 / -1;
        min-height: 118px;
      }
      .label {
        margin-bottom: 8px;
        color: #5F5E5A;
        font-size: 11px;
        font-weight: 900;
        letter-spacing: 0.12em;
        text-transform: uppercase;
      }
      .value {
        color: #2C2C2A;
        font-size: 15px;
        font-weight: 750;
        line-height: 1.55;
        overflow-wrap: anywhere;
      }
      .footer {
        display: flex;
        justify-content: space-between;
        gap: 24px;
        margin-top: 28px;
        border-top: 1px solid #E5EEE9;
        padding-top: 18px;
        color: #5F5E5A;
        font-size: 12px;
        line-height: 1.6;
      }
      .accent { color: #EB6834; font-weight: 900; }
      @media print {
        body { background: white; }
        .sheet {
          min-height: auto;
          border-radius: 0;
          box-shadow: none;
        }
      }
    </style>
  </head>
  <body>
    <main class="sheet">
      <section class="hero">
        <div class="hero-content">
          <div class="brand"><span class="logo">NS</span><span>NagarSeva</span></div>
          <h1>${safeTitle}</h1>
          <p class="subtitle">Premium civic issue report generated from the citizen dashboard for municipal review, assignment, and resolution tracking.</p>
          <div class="badge-row">
            <span class="badge">AI assisted complaint</span>
            <span class="badge">Citizen submitted</span>
            <span class="badge">Evidence tracked</span>
          </div>
        </div>
      </section>
      <section class="content">
        <h2 class="section-title">Issue Details</h2>
        <div class="grid">${reportRows}</div>
        <div class="footer">
          <div><strong>NagarSeva</strong><br />Civic Issues. Fixed. Transparently.</div>
          <div><span class="accent">Note:</span> This report contains the submitted metadata and uploaded image file name for verification.</div>
        </div>
      </section>
    </main>
    <script>
      window.addEventListener('load', () => {
        setTimeout(() => window.print(), 250);
      });
    </script>
  </body>
</html>`

  if (!printWindow) {
    const blob = new Blob([html], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'nagarseva-issue-report.html'
    link.click()
    URL.revokeObjectURL(url)
    return
  }

  printWindow.document.open()
  printWindow.document.write(html)
  printWindow.document.close()
}
