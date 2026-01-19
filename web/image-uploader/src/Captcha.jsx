import ReCAPTCHA from 'react-google-recaptcha';

export default function Captcha({ siteKey, onVerify }) {
  return (
    <ReCAPTCHA
      sitekey={siteKey}
      onChange={(token) => onVerify(token)}
      onExpired={() => onVerify(null)}
    />
  );
}
