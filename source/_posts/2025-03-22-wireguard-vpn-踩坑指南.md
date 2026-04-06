---
layout: post
title: "WireGuard VPN 配置完全踩坑指南"
date: 2025-03-22 10:54:00 +0800
categories: 网络
tags: [WireGuard, VPN, 踩坑]
---

# WireGuard VPN 配置完全踩坑指南

## 一、问题背景

搭建一台 WireGuard VPN 服务器（Linux），客户端使用 macOS + WireGuard 官方客户端。能成功建立隧道连接（`wg show` 显示 handshake 正常），但**无法访问互联网**，DNS 解析失败。

<!-- more -->

---

## 二、症状清单

1. 能 ping 通 VPN 服务器虚拟 IP（`10.0.0.1`）
2. 无法 ping 外网 IP（`ping 8.8.8.8` 超时）
3. DNS 解析失败（`dig google.com` 无响应）
4. `curl ifconfig.me` 超时
5. 客户端路由表：默认网关仍走本地（`en1`），而非 `utun4`

---

## 三、排查过程与踩坑点

### 坑 1：客户端 AllowedIPs 配置错误

**现象：**  
`wg show` 显示 `allowed ips: 10.0.0.2/32`

**原因：**  
客户端的 `[Peer]` 配置中 `AllowedIPs` 设置为 `10.0.0.2/32`，表示**只有访问 `10.0.0.2` 的流量才走 VPN**。

**解决：**  
改为 `AllowedIPs = 0.0.0.0/0`（所有 IPv4 流量走 VPN）：

```ini
[Peer]
PublicKey = <服务器公钥>
Endpoint = <服务器IP>:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

**验证：**  
重启 WG 后 `wg show` 应显示 `allowed ips: 0.0.0.0/0`

---

### 坑 2：macOS DNS 配置不自动应用

**现象：**  
即使配置文件中有 `DNS = 1.1.1.1, 8.8.8.8`，`/etc/resolv.conf` 仍然显示本地 DNS（`192.168.0.1`）。

**原因：**  
macOS 使用 `scutil` 管理 DNS，不会自动读取 WireGuard 的 DNS 设置。

**解决：**  
手动设置系统 DNS：

```bash
sudo networksetup -setdnsservers "Wi-Fi" 1.1.1.1 8.8.8.8
```

或添加 PostUp 脚本（需要 sudoers 配置）：

```ini
PostUp = sudo networksetup -setdnsservers "Wi-Fi" 1.1.1.1 8.1.1.1
PostDown = sudo networksetup -setdnsservers "Wi-Fi" Empty
```

---

### 坑 3：服务端缺少 NAT 转发

**现象：**  
隧道握手正常，抓包有双向 UDP 通信，但客户端 ping 外网 IP 超时。

**原因：**  
服务端 IP 转发或 NAT 规则未配置，收到的 `10.0.0.2` 流量无法转发到外网。

**解决：**  
在服务端配置 NAT 并启用 IP 转发：

```bash
# 1. 启用 IP 转发
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-wg.conf
sudo sysctl -p /etc/sysctl.d/99-wg.conf

# 2. 添加 iptables NAT 规则（修改接口名）
sudo iptables -t nat -A POSTROUTING -o enp1s0 -j MASQUERADE
sudo iptables -A FORWARD -i wg0 -j ACCEPT
```

持久化（保存规则）：
```bash
# Ubuntu/Debian
sudo netfilter-persistent save

# CentOS/RHEL
sudo service iptables save
```

或在 `wg0.conf` 中配置：

```ini
[Interface]
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o enp1s0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o enp1s0 -j MASQUERADE
```

**注意：** `enp1s0` 必须替换为实际的外网接口名（用 `ip link show` 查看）。这是我踩的最大的坑——配置成了 `eth0`，结果一直不生效！

---

### 坑 4：MTU 导致 DNS 查询失败

**现象：**  
`dig @1.1.1.1 google.com` 超时，但 `ping 1.1.1.1` 正常。

**原因：**  
WireGuard 默认 MTU 1420，加上 UDP 封装后可能超过链路的 MTU，导致大包（如 DNS 查询超过 512 字节）丢包。

**解决：**  
降低 MTU 到 1280：

```ini
[Interface]
MTU = 1280
```

或根据实际情况调整（1200~1400 之间）。

---

### 坑 5：服务端 IP 转发未启用

**现象：**  
NAT 规则已加，但客户端仍无法访问。

**检查：**
```bash
sysctl net.ipv4.ip_forward  # 应为 1
```

**解决：**
```bash
echo 'net.ipv4.ip_forward=1' | sudo tee /etc/sysctl.d/99-wg.conf
sudo sysctl -p /etc/sysctl.d/99-wg.conf
```

---

## 四、完整配置示例

### 服务端 `/etc/wireguard/wg0.conf`

```ini
[Interface]
PrivateKey = <服务器私钥>
Address = 10.0.0.1/24
ListenPort = 51820
# 关键：外网接口名必须正确（通过 ip link show 查看）
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o enp1s0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o enp1s0 -j MASQUERADE

[Peer]
PublicKey = <客户端公钥>
AllowedIPs = 10.0.0.2/32
```

### 客户端 `/etc/wireguard/wg0.conf`

```ini
[Interface]
PrivateKey = <客户端私钥>
Address = 10.0.0.2/24
DNS = 1.1.1.1, 8.8.8.8
MTU = 1280

[Peer]
PublicKey = <服务器公钥>
Endpoint = <服务器公网IP>:51820
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
```

---

## 五、验证步骤

```bash
# 服务端
sudo wg-quick down wg0 && sudo wg-quick up wg0
sudo wg show

# 客户端
sudo wg-quick down wg0 && sudo wg-quick up wg0
wg show | grep "allowed ips"  # 确认是 0.0.0.0/0
netstat -rn | grep default    # 确认走 utun

# 测试
ping -c 3 8.8.8.8
dig google.com
curl ifconfig.me  # 应显示服务器 IP
```

---

## 六、总结

WireGuard 配置虽然简单，但三个关键点缺一不可：

1. **客户端 `AllowedIPs`** → 决定哪些流量走 VPN
2. **服务端 IP 转发 + NAT** → 让客户端流量能出去并返回
3. **DNS 配置** → macOS 需手动设置

按这个清单逐项检查，应该能搞定大部分 WireGuard 上网问题。

---

**最坑的一点：** NAT 规则的 `-o` 参数必须是服务端**实际的外网接口名**，不能想当然地写成 `eth0`。  
用 `ip link show` 确认接口名，这是配置成功的关键！

---

*发布于 2025-03-22，记录一次完整的 WireGuard 排错过程。*