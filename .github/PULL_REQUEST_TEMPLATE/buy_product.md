---
name: 🛒 Buy Product
about: 提交ETH付款后，使用此模板下单。系统会自动验证链上交易并在PR评论中交付产品。
title: "[BUY] <产品名称>"
labels: payment-pending
---

## 产品信息

- **产品名称**: AI Creator Efficiency Dashboard

  > 当前可购买产品:
  > | 产品 | 价格 |
  > |------|------|
  > | AI Creator Efficiency Dashboard | $9 (0.003 ETH) |
  >
  > 更多产品请查看 [product_config.json](../blob/main/product_config.json)

## 付款信息

- **付款金额**: 0.003 ETH
- **付款哈希**: 0x...（必填，长度66个字符，以0x开头）
- **付款时间戳**: （可选）
- **我的钱包地址**: 0x...（必填，请填写你**发起这笔交易**的地址）

## 备注（可选）

---

### ✅ 提交前检查清单

请逐项确认，否则验证将失败：

- [ ] 我已向收款地址 `0x2cb55e288c404daf69d4cacbeadd9ae3aba25ffb` 转账 **0.003 ETH** 或等值金额
- [ ] 付款哈希以 `0x` 开头，共 66 个字符（0x + 64位十六进制）
- [ ] 我填写的钱包地址 **就是发起这笔交易的钱包地址**（系统会用这个地址与链上交易发起方比对，不匹配将验证失败）

> 💡 不知道怎么操作？先付款 → 在 MetaMask 或区块浏览器中找到这笔交易的哈希 → 复制粘贴到上面
