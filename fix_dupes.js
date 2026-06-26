const fs = require('fs');
let t = fs.readFileSync('template_editable.html', 'utf8');

console.log('Before - toggleLang count:', (t.match(/toggleLang/g)||[]).length);
console.log('Before - rad-top-btn count:', (t.match(/rad-top-btn/g)||[]).length);

// The template has the buttons injected TWICE inside the scrollRef div.
// Strategy: find all rad-fab buttons and keep only the LAST set (most recent/correct).
// The duplicates appear right after the scrollRef opening div.
// We'll remove everything between the scrollRef open tag and the first non-button content,
// then re-insert a single clean set.

// Find the scrollRef div open tag
const scrollRx = /<div[^>]*ref="\{\{ scrollRef \}\}"[^>]*>/;
const scrollMatch = t.match(scrollRx);
if (!scrollMatch) { console.log('scrollRef not found!'); process.exit(1); }

const scrollEnd = scrollMatch.index + scrollMatch[0].length;

// Find where the actual page content starts (after all the rad-fab buttons)
// The buttons end before the <div style="padding: that wraps the logo
const contentStart = t.indexOf('\n\n      <div style="padding:', scrollEnd);
if (contentStart < 0) { console.log('Content div not found!'); process.exit(1); }

const btnSection = t.substring(scrollEnd, contentStart);
console.log('\n--- Current button section (between scrollRef and content) ---');
console.log('Length:', btnSection.length);
console.log('toggleLang in section:', (btnSection.match(/toggleLang/g)||[]).length);

// Build ONE clean set of buttons
const fabStyle = 'position:fixed;z-index:9000;width:52px;height:52px;border-radius:50%;background:var(--chip);border:1.5px solid var(--line);color:var(--ink);cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 14px rgba(0,0,0,0.13);padding:0;';
const cleanBtns = `
      <button class="rad-fab" onclick="{{ toggleLang }}" aria-label="{{ langLabel }}" style="${fabStyle}top:16px;right:16px;flex-direction:column;gap:2px;"><svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M2 12h20"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg><span style="font-size:8px;font-weight:800;letter-spacing:.12em;line-height:1;font-family:Manrope,sans-serif;">{{ langLabel }}</span></button>
      <button class="rad-fab" onclick="{{ toggleTheme }}" aria-label="Toggle theme" style="${fabStyle}bottom:88px;right:16px;font-size:22px;line-height:1;">{{ themeIcon }}</button>
      <button class="rad-fab rad-top" id="rad-top-btn" style="${fabStyle}bottom:152px;right:16px;font-size:20px;font-weight:700;line-height:1;">&#8593;</button>`;

// Also find and remove duplicate scroll-to-top scripts (keep only one)
// Replace entire button section with clean single set
t = t.substring(0, scrollEnd) + cleanBtns + t.substring(contentStart);

// Remove any duplicate scroll-to-top scripts - keep only the last one
const scriptMarker = '<script>\n(function(){';
const scriptEnd = '})();\n</script>';
const firstScript = t.indexOf(scriptMarker);
const lastScript = t.lastIndexOf(scriptMarker);
if (firstScript !== lastScript) {
  // Remove all but the last
  const lastEnd = t.indexOf(scriptEnd, lastScript) + scriptEnd.length;
  const firstEnd = t.indexOf(scriptEnd, firstScript) + scriptEnd.length;
  // Remove first occurrence
  t = t.substring(0, firstScript) + t.substring(firstEnd);
  console.log('Removed duplicate scroll script');
}

// Verify
console.log('\nAfter - toggleLang count:', (t.match(/toggleLang/g)||[]).length);
console.log('After - rad-top-btn count:', (t.match(/rad-top-btn/g)||[]).length);
console.log('After - scroll script count:', (t.match(/<script>\n\(function\(\)\{/g)||[]).length);

fs.writeFileSync('template_editable.html', t, 'utf8');
console.log('\nSaved template_editable.html');
