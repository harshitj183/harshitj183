
  <script src="https://cdn.statically.io/gh/harshitj183/harshitj183/main/badge.js" </script>

// Create the badge element
const badge = document.createElement('div');
badge.classList.add('badge');

// Create the logo element
const logo = document.createElement('img');
logo.classList.add('logo');
logo.src = 'profileLOgo.png';
logo.alt = 'Google logo';

// Create the text element
const text = document.createElement('div');
text.classList.add('text');

// Create the partner element
const partner = document.createElement('span');
partner.classList.add('partner');
partner.textContent = '@harshitj183';

// Create the text node for "Developed by"
const developedBy = document.createTextNode('Developed by');

// Append the elements to the page
text.appendChild(developedBy);
text.appendChild(partner);
badge.appendChild(logo);
badge.appendChild(text);
document.body.appendChild(badge);

// Add the CSS styles
badge.style.position = 'fixed';
badge.style.bottom = '10px';
badge.style.right = '10px';
badge.style.display = 'flex';
badge.style.alignItems = 'center';
badge.style.padding = '2px';
badge.style.backgroundColor = '#4285f4';
badge.style.border = '1px solid #4285f4';
badge.style.borderRadius = '3px';
badge.style.fontSize = '10px';
badge.style.color = '#fff';
badge.style.width = '150px';
badge.style.height = '30px';

logo.style.position = 'absolute';
logo.style.top = '-10px';
logo.style.left = '-10px';
logo.style.width = '50px';
logo.style.height = '50px';
logo.style.borderRadius = '25%';
logo.style.border = '2px solid #fff';
logo.style.borderBottom = '2px solid #4285f4';
logo.style.borderRadius = '50% 50% 50% 50%/60% 60% 40% 40%';

text.style.display = 'flex';
text.style.flexDirection = 'column';
text.style.alignItems = 'flex-start';
text.style.marginLeft = '50px';

partner.style.color = '#fff';
partner.style.fontWeight = 'bold';
partner.style.display = 'block';
