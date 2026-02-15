function AboutPage() {
    return (
        <div className="home-container animate-fade-in" style={{ maxWidth: '800px', textAlign: 'left' }}>
            <div className="glass-card">
                <h2 style={{ fontSize: '2rem', marginBottom: '20px', color: 'white' }}>About Civic Issue Management</h2>

                <section style={{ marginBottom: '30px' }}>
                    <h3 style={{ color: '#a855f7', marginBottom: '10px' }}>Our Mission</h3>
                    <p style={{ color: '#cbd5e1', lineHeight: '1.6' }}>
                        We empower citizens to report civic issues directly to municipal authorities. By leveraging technology, we ensure faster resolutions and greater transparency in local governance.
                    </p>
                </section>

                <section style={{ marginBottom: '30px' }}>
                    <h3 style={{ color: '#a855f7', marginBottom: '10px' }}>How It Works</h3>
                    <ol style={{ paddingLeft: '20px', color: '#cbd5e1', lineHeight: '1.8' }}>
                        <li><strong>Report:</strong> Take a photo and describe the issue. Our AI categorizes it automatically.</li>
                        <li><strong>Track:</strong> Monitor the status of your complaint in real-time.</li>
                        <li><strong>Resolve:</strong> Authorities act on the issue and update its progress.</li>
                    </ol>
                </section>

                <section>
                    <h3 style={{ color: '#a855f7', marginBottom: '10px' }}>Contact Support</h3>
                    <p style={{ color: '#cbd5e1' }}>
                        Available Mon-Fri, 9am - 5pm<br />
                        Email: <a href="mailto:support@civicapp.com" style={{ color: '#60a5fa' }}>support@civicapp.com</a><br />
                        Phone: +1 234 567 890
                    </p>
                </section>
            </div>
        </div>
    );
}

export default AboutPage;
