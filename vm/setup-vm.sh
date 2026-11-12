#!/bin/bash
set -e
PUBKEY='ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMnCNV68bQ74c50P+ys3DCuKQeF1mld/Z/aBbO35yl0G lab13-vm'

# student account with passwordless sudo (classroom VM)
if ! id student >/dev/null 2>&1; then
  useradd -m -s /bin/bash student
  echo 'student:Lab13vm2026' | chpasswd
  usermod -aG sudo student
fi
echo 'student ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/student
chmod 440 /etc/sudoers.d/student

install -d -m 700 -o student -g student /home/student/.ssh
echo "$PUBKEY" > /home/student/.ssh/authorized_keys
chown student:student /home/student/.ssh/authorized_keys
chmod 600 /home/student/.ssh/authorized_keys

systemctl enable --now ssh >/dev/null 2>&1 || systemctl enable --now sshd >/dev/null 2>&1 || true
systemctl restart ssh >/dev/null 2>&1 || true

# lighter prompts for screenshots
cat > /home/student/.bashrc <<'EOF'
export PS1='student@ubuntu-server:~$ '
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
cd ~
EOF
chown student:student /home/student/.bashrc

hostnamectl set-hostname ubuntu-server
echo "SETUP_OK"
ss -tlnp | grep ':22' || true
