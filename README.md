# Demo Projects

This repository hosts two demonstration projects focused on web security: Multi-Factor Authentication using Time-based One-Time Passwords (MFA-TOTP) and securing web applications using NGINX with Client Authentication Certificates (CAC). Each demo is contained in its own folder and includes a dedicated README file with detailed setup and usage instructions.

## [MFA-TOTP Demo](./mfa-totp)

The MFA-TOTP demo showcases how to enhance the security of a web application by integrating Multi-Factor Authentication with Time-based One-Time Passwords. It is built using the Flask framework and demonstrates key concepts of MFA including generating TOTP tokens, scanning QR codes for MFA setup, and validating tokens for secure access.

## [MFA-CAC Demo](./mfa-cac)

The MFA-CAC demo demonstrates how to configure NGINX to secure a web application using Client Authentication Certificates (CAC), ensuring that only clients with a valid certificate can access the application. This approach adds an additional layer of security by verifying the client's identity at the network level.
