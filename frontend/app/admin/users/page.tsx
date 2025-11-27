"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api/client";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Trash2, Edit, KeyRound, UserPlus, LogOut, Shield } from "lucide-react";

interface User {
  id: number;
  username: string;
  email?: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export default function AdminUsersPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuthStore();
  const { toast } = useToast();
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isResetPasswordDialogOpen, setIsResetPasswordDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [deletingUserId, setDeletingUserId] = useState<number | null>(null);
  const [resettingPasswordUserId, setResettingPasswordUserId] = useState<number | null>(null);

  // 检查管理员权限
  useEffect(() => {
    if (!isAuthenticated || !user || (user.role !== "admin" && user.role !== "superadmin")) {
      router.push("/admin/login");
      return;
    }
    loadUsers();
  }, [isAuthenticated, user, router]);

  const loadUsers = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const { token } = useAuthStore.getState();
      if (!token) {
        router.push("/admin/login");
        return;
      }
      
      const data = await apiGet<User[]>("/api/auth/admin/users");
      setUsers(data);
    } catch (err: any) {
      const errorMessage = err.detail || "加载用户列表失败";
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "加载失败",
        description: errorMessage,
      });
      // 如果是 401 或 403 错误，重定向到登录页
      if (err.status === 401 || err.status === 403) {
        setTimeout(() => {
          useAuthStore.getState().logout();
          router.push("/admin/login");
        }, 100);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateUser = async (formData: FormData) => {
    try {
      const newUser = {
        username: formData.get("username") as string,
        password: formData.get("password") as string,
        email: formData.get("email") as string || undefined,
        role: formData.get("role") as string || "user",
        is_active: true,
      };
      await apiPost("/api/auth/admin/users", newUser);
      setIsCreateDialogOpen(false);
      toast({
        title: "创建成功",
        description: `用户 "${newUser.username}" 已成功创建`,
      });
      loadUsers();
    } catch (err: any) {
      const errorMessage = err.detail || "创建用户失败";
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "创建失败",
        description: errorMessage,
      });
    }
  };

  const handleUpdateUser = async (formData: FormData) => {
    if (!editingUser) return;
    try {
      const updates: any = {};
      const email = formData.get("email") as string;
      const role = formData.get("role") as string;
      const is_active = formData.get("is_active") === "true";

      if (email !== editingUser.email) updates.email = email || null;
      if (role !== editingUser.role) updates.role = role;
      if (is_active !== editingUser.is_active) updates.is_active = is_active;

      await apiPut(`/api/auth/admin/users/${editingUser.id}`, updates);
      setIsEditDialogOpen(false);
      setEditingUser(null);
      toast({
        title: "更新成功",
        description: `用户 "${editingUser.username}" 的信息已更新`,
      });
      loadUsers();
    } catch (err: any) {
      const errorMessage = err.detail || "更新用户失败";
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "更新失败",
        description: errorMessage,
      });
    }
  };

  const handleDeleteUser = async (userId: number) => {
    try {
      await apiDelete(`/api/auth/admin/users/${userId}`);
      setDeletingUserId(null);
      toast({
        title: "删除成功",
        description: "用户已成功删除",
      });
      loadUsers();
    } catch (err: any) {
      const errorMessage = err.detail || "删除用户失败";
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "删除失败",
        description: errorMessage,
      });
    }
  };

  const handleResetPassword = async (formData: FormData) => {
    if (!resettingPasswordUserId) return;
    try {
      const newPassword = formData.get("new_password") as string;
      await apiPost(`/api/auth/admin/users/${resettingPasswordUserId}/reset-password`, {
        new_password: newPassword,
      });
      setIsResetPasswordDialogOpen(false);
      setResettingPasswordUserId(null);
      toast({
        title: "密码重置成功",
        description: "用户密码已成功重置",
      });
    } catch (err: any) {
      const errorMessage = err.detail || "重置密码失败";
      setError(errorMessage);
      toast({
        variant: "destructive",
        title: "重置失败",
        description: errorMessage,
      });
    }
  };

  const getRoleBadgeVariant = (role: string) => {
    switch (role) {
      case "superadmin":
        return "destructive";
      case "admin":
        return "secondary";
      default:
        return "outline";
    }
  };

  const getRoleLabel = (role: string) => {
    switch (role) {
      case "superadmin":
        return "超级管理员";
      case "admin":
        return "管理员";
      default:
        return "普通用户";
    }
  };

  if (!isAuthenticated || !user || (user.role !== "admin" && user.role !== "superadmin")) {
    return null;
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* 页面头部 */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">用户管理</h1>
          <p className="text-muted-foreground mt-1">管理系统中的所有用户账户</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Shield className="h-4 w-4" />
            <span>{user.username}</span>
            <Badge variant={getRoleBadgeVariant(user.role)}>{getRoleLabel(user.role)}</Badge>
          </div>
          <Button variant="outline" onClick={() => { logout(); router.push("/"); }}>
            <LogOut className="h-4 w-4 mr-2" />
            退出
          </Button>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* 用户列表卡片 */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>用户列表</CardTitle>
              <CardDescription>共 {users.length} 个用户</CardDescription>
            </div>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <UserPlus className="h-4 w-4 mr-2" />
                  创建用户
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>创建新用户</DialogTitle>
                  <DialogDescription>填写用户信息以创建新账户</DialogDescription>
                </DialogHeader>
                <form action={handleCreateUser} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="create-username">用户名</Label>
                    <Input id="create-username" name="username" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="create-password">密码</Label>
                    <Input id="create-password" name="password" type="password" required />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="create-email">邮箱（可选）</Label>
                    <Input id="create-email" name="email" type="email" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="create-role">角色</Label>
                    <Select name="role" defaultValue="user">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="user">普通用户</SelectItem>
                        {user.role === "superadmin" && (
                          <>
                            <SelectItem value="admin">管理员</SelectItem>
                            <SelectItem value="superadmin">超级管理员</SelectItem>
                          </>
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                  <Button type="submit" className="w-full">创建</Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-12 w-12 rounded-full" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-[250px]" />
                    <Skeleton className="h-4 w-[200px]" />
                  </div>
                </div>
              ))}
            </div>
          ) : users.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>暂无用户数据</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-center">ID</TableHead>
                    <TableHead className="text-center">用户名</TableHead>
                    <TableHead className="text-center">邮箱</TableHead>
                    <TableHead className="text-center">角色</TableHead>
                    <TableHead className="text-center">状态</TableHead>
                    <TableHead className="text-center">创建时间</TableHead>
                    <TableHead className="text-center">操作</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {users.map((u) => (
                    <TableRow key={u.id}>
                      <TableCell className="font-mono text-sm text-center">{u.id}</TableCell>
                      <TableCell className="font-medium text-center">{u.username}</TableCell>
                      <TableCell className="text-center">{u.email || <span className="text-muted-foreground">-</span>}</TableCell>
                      <TableCell className="text-center">
                        <Badge variant={getRoleBadgeVariant(u.role)}>
                          {getRoleLabel(u.role)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-center">
                        <Badge variant={u.is_active ? "success" : "outline"}>
                          {u.is_active ? "激活" : "禁用"}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground text-center">
                        {new Date(u.created_at).toLocaleString("zh-CN")}
                      </TableCell>
                      <TableCell>
                        <div className="flex justify-center gap-2">
                          <Dialog 
                            open={isEditDialogOpen && editingUser?.id === u.id} 
                            onOpenChange={(open) => {
                              setIsEditDialogOpen(open);
                              if (open) setEditingUser(u);
                              else setEditingUser(null);
                            }}
                          >
                            <DialogTrigger asChild>
                              <Button variant="outline" size="sm">
                                <Edit className="h-4 w-4 mr-1" />
                                编辑
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>编辑用户</DialogTitle>
                                <DialogDescription>修改用户信息</DialogDescription>
                              </DialogHeader>
                              <form action={handleUpdateUser} className="space-y-4">
                                <div className="space-y-2">
                                  <Label htmlFor="edit-email">邮箱</Label>
                                  <Input
                                    id="edit-email"
                                    name="email"
                                    type="email"
                                    defaultValue={u.email || ""}
                                  />
                                </div>
                                <div className="space-y-2">
                                  <Label htmlFor="edit-role">角色</Label>
                                  <Select name="role" defaultValue={u.role}>
                                    <SelectTrigger>
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="user">普通用户</SelectItem>
                                      {user.role === "superadmin" && (
                                        <>
                                          <SelectItem value="admin">管理员</SelectItem>
                                          <SelectItem value="superadmin">超级管理员</SelectItem>
                                        </>
                                      )}
                                    </SelectContent>
                                  </Select>
                                </div>
                                <div className="space-y-2">
                                  <Label htmlFor="edit-is_active">状态</Label>
                                  <Select name="is_active" defaultValue={u.is_active ? "true" : "false"}>
                                    <SelectTrigger>
                                      <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                      <SelectItem value="true">激活</SelectItem>
                                      <SelectItem value="false">禁用</SelectItem>
                                    </SelectContent>
                                  </Select>
                                </div>
                                <Button type="submit" className="w-full">保存</Button>
                              </form>
                            </DialogContent>
                          </Dialog>

                          <Dialog
                            open={isResetPasswordDialogOpen && resettingPasswordUserId === u.id}
                            onOpenChange={(open) => {
                              setIsResetPasswordDialogOpen(open);
                              if (open) setResettingPasswordUserId(u.id);
                              else setResettingPasswordUserId(null);
                            }}
                          >
                            <DialogTrigger asChild>
                              <Button variant="outline" size="sm">
                                <KeyRound className="h-4 w-4 mr-1" />
                                重置密码
                              </Button>
                            </DialogTrigger>
                            <DialogContent>
                              <DialogHeader>
                                <DialogTitle>重置密码</DialogTitle>
                                <DialogDescription>
                                  为用户 "{u.username}" 设置新密码
                                </DialogDescription>
                              </DialogHeader>
                              <form action={handleResetPassword} className="space-y-4">
                                <div className="space-y-2">
                                  <Label htmlFor="new-password">新密码</Label>
                                  <Input
                                    id="new-password"
                                    name="new_password"
                                    type="password"
                                    required
                                    minLength={6}
                                  />
                                </div>
                                <Button type="submit" className="w-full">重置密码</Button>
                              </form>
                            </DialogContent>
                          </Dialog>

                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => setDeletingUserId(u.id)}
                                disabled={u.id === user.id}
                              >
                                <Trash2 className="h-4 w-4 mr-1" />
                                删除
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>确认删除</AlertDialogTitle>
                                <AlertDialogDescription>
                                  确定要删除用户 <strong>"{u.username}"</strong> 吗？此操作无法撤销。
                                  {u.id === user.id && (
                                    <span className="block mt-2 text-destructive font-medium">
                                      不能删除当前登录的用户
                                    </span>
                                  )}
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>取消</AlertDialogCancel>
                                <AlertDialogAction
                                  onClick={() => {
                                    if (u.id !== user.id) {
                                      handleDeleteUser(u.id);
                                    }
                                  }}
                                  disabled={u.id === user.id}
                                  className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                                >
                                  删除
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
