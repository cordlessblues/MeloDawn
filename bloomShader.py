import moderngl
import pygame
import numpy as np
import io

# --- GLSL Shader Code ---

# Basic Vertex Shader for a fullscreen quad
vertex_shader = """
#version 330 core
in vec2 in_vert;
in vec2 in_texcoord;
out vec2 v_texcoord;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    // Flip the y-coordinate of the texture
    v_texcoord = vec2(in_texcoord.x, 1.0 - in_texcoord.y);
}
"""

# Fragment Shader for Horizontal Gaussian Blur (Simplified)
# Now directly blurs the input texture
horizontal_blur_fragment_shader = """
#version 330 core
in vec2 v_texcoord;
out vec4 f_color;
uniform sampler2D u_texture;
uniform float u_resolution_x;
uniform float u_blur_amount; // Roughly corresponds to the blur radius

void main() {
    vec4 sum = vec4(0.0);
    float pixel_size_x = u_blur_amount / u_resolution_x;

    // Simple approximation of Gaussian blur by sampling nearby pixels
    sum += texture(u_texture, v_texcoord + vec2(-4.0 * pixel_size_x, 0.0)) * 0.00443;
    sum += texture(u_texture, v_texcoord + vec2(-3.0 * pixel_size_x, 0.0)) * 0.05400;
    sum += texture(u_texture, v_texcoord + vec2(-2.0 * pixel_size_x, 0.0)) * 0.24200;
    sum += texture(u_texture, v_texcoord + vec2(-1.0 * pixel_size_x, 0.0)) * 0.36910;
    sum += texture(u_texture, v_texcoord + vec2( 0.0 * pixel_size_x, 0.0)) * 0.60650; // Center pixel weight (approx)
    sum += texture(u_texture, v_texcoord + vec2( 1.0 * pixel_size_x, 0.0)) * 0.36910;
    sum += texture(u_texture, v_texcoord + vec2( 2.0 * pixel_size_x, 0.0)) * 0.24200;
    sum += texture(u_texture, v_texcoord + vec2( 3.0 * pixel_size_x, 0.0)) * 0.05400;
    sum += texture(u_texture, v_texcoord + vec2( 4.0 * pixel_size_x, 0.0)) * 0.00443;

    // Normalize by the sum of weights (approximate)
    f_color = sum / (2.0 * (0.00443 + 0.05400 + 0.24200 + 0.36910) + 0.60650);
}
"""

# Fragment Shader for Vertical Gaussian Blur (Simplified)
# Now directly blurs the input texture
vertical_blur_fragment_shader = """
#version 330 core
in vec2 v_texcoord;
out vec4 f_color;
uniform sampler2D u_texture;
uniform float u_resolution_y;
uniform float u_blur_amount;

void main() {
    vec4 sum = vec4(0.0);
    float pixel_size_y = u_blur_amount / u_resolution_y;

    sum += texture(u_texture, v_texcoord + vec2(0.0, -4.0 * pixel_size_y)) * 0.00443;
    sum += texture(u_texture, v_texcoord + vec2(0.0, -3.0 * pixel_size_y)) * 0.05400;
    sum += texture(u_texture, v_texcoord + vec2(0.0, -2.0 * pixel_size_y)) * 0.24200;
    sum += texture(u_texture, v_texcoord + vec2(0.0, -1.0 * pixel_size_y)) * 0.36910;
    sum += texture(u_texture, v_texcoord + vec2(0.0,  0.0 * pixel_size_y)) * 0.60650;
    sum += texture(u_texture, v_texcoord + vec2(0.0,  1.0 * pixel_size_y)) * 0.36910;
    sum += texture(u_texture, v_texcoord + vec2(0.0,  2.0 * pixel_size_y)) * 0.24200;
    sum += texture(u_texture, v_texcoord + vec2(0.0,  3.0 * pixel_size_y)) * 0.05400;
    sum += texture(u_texture, v_texcoord + vec2(0.0,  4.0 * pixel_size_y)) * 0.00443;

    f_color = sum / (2.0 * (0.00443 + 0.05400 + 0.24200 + 0.36910) + 0.60650);
}
"""

# Fragment Shader for Combining (Additive)
combine_fragment_shader = """
#version 330 core
in vec2 v_texcoord;
out vec4 f_color;
uniform sampler2D u_original_texture;
uniform sampler2D u_blurred_texture;
void main() {
    vec4 original_color = texture(u_original_texture, v_texcoord);
    vec4 blurred_color = texture(u_blurred_texture, v_texcoord);
    // Add the blurred color to the original, preserving original alpha
    f_color = vec4(original_color.rgb + blurred_color.rgb, original_color.a);
}
"""

class BloomShader:
    def __init__(self, ctx: moderngl.Context, surface_size: tuple[int, int]):
        self.ctx = ctx
        self.surface_size = surface_size
        width, height = surface_size

        # --- Create Shader Programs ---
        # No brightness extraction program needed
        self.horizontal_blur_program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=horizontal_blur_fragment_shader)
        self.vertical_blur_program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=vertical_blur_fragment_shader)
        self.combine_program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=combine_fragment_shader)

        # --- Create Geometry (Fullscreen Quad) ---
        quad_vertices = np.array([
            -1.0, -1.0,  0.0, 0.0,  # Bottom Left
             1.0, -1.0,  1.0, 0.0,  # Bottom Right
             1.0,  1.0,  1.0, 1.0,  # Top Right
            -1.0,  1.0,  0.0, 1.0   # Top Left
        ], dtype='f4')

        quad_indices = np.array([0, 1, 2, 2, 3, 0], dtype='i4')

        self.vbo = self.ctx.buffer(quad_vertices.tobytes())
        self.ibo = self.ctx.buffer(quad_indices.tobytes())

        content = [
            (self.vbo, '2f 2f', 'in_vert', 'in_texcoord')
        ]

        # VAOs for the remaining programs
        self.horizontal_blur_vao = self.ctx.vertex_array(self.horizontal_blur_program, content, self.ibo)
        self.vertical_blur_vao = self.ctx.vertex_array(self.vertical_blur_program, content, self.ibo)
        self.combine_vao = self.ctx.vertex_array(self.combine_program, content, self.ibo)

        # --- Create Textures and Framebuffers ---
        # Only need textures for horizontal and vertical blur
        self.texture_horizontal_blur = self.ctx.texture((width, height), 4)
        self.texture_vertical_blur = self.ctx.texture((width, height), 4)

        # Framebuffers for horizontal and vertical blur
        self.fbo_horizontal_blur = self.ctx.framebuffer(color_attachments=[self.texture_horizontal_blur])
        self.fbo_vertical_blur = self.ctx.framebuffer(color_attachments=[self.texture_vertical_blur])

    def apply_bloom(self, surface: pygame.Surface, blur_amount: float = 5.0) -> pygame.Surface:
        """
        Applies a bloom effect (full image blur + additive blend) to the surface.
        No brightness exclusion.

        Args:
            surface: The Pygame surface to apply the bloom effect to.
                     Must have an alpha channel.
            blur_amount: Controls the intensity/radius of the blur.

        Returns:
            A new Pygame surface with the bloom effect applied.
        """
        width, height = surface.get_size()
        if (width, height) != self.surface_size:
            print("Warning: Surface size mismatch. Recreating bloom shader.")
            self.__init__(self.ctx, (width, height))

        if surface.get_bitsize() != 32 or surface.get_masks() != (0xff000000, 0x00ff0000, 0x0000ff00, 0x000000ff):
             surface = surface.convert_alpha()

        try:
            texture_original = self.ctx.texture(surface.get_size(), 4, surface.get_buffer().raw)
        except moderngl.Error:
            print("Direct Pygame buffer to ModernGL texture failed, falling back to byte string.")
            img_str = pygame.image.tostring(surface, "RGBA", True)
            texture_original = self.ctx.texture(surface.get_size(), 4, img_str)

        # --- Bloom Effect Passes (Simplified) ---

        # Pass 1: Horizontal Blur (directly on the original texture)
        self.ctx.fbo = self.fbo_horizontal_blur
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.horizontal_blur_program['u_texture'] = 0
        texture_original.use(0) # Blur the original texture
        self.horizontal_blur_program['u_resolution_x'] = float(width)
        self.horizontal_blur_program['u_blur_amount'] = blur_amount
        self.horizontal_blur_vao.render()

        # Pass 2: Vertical Blur (on the horizontally blurred texture)
        self.ctx.fbo = self.fbo_vertical_blur
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.vertical_blur_program['u_texture'] = 0
        self.texture_horizontal_blur.use(0) # Blur the horizontally blurred texture
        self.vertical_blur_program['u_resolution_y'] = float(height)
        self.vertical_blur_program['u_blur_amount'] = blur_amount
        self.vertical_blur_vao.render()

        # Pass 3: Combine with Original onto an intermediate texture
        intermediate_combined_texture = self.ctx.texture((width, height), 4)
        fbo_intermediate_combined = self.ctx.framebuffer(color_attachments=[intermediate_combined_texture])

        self.ctx.fbo = fbo_intermediate_combined
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        self.combine_program['u_original_texture'] = 0
        self.combine_program['u_blurred_texture'] = 1
        texture_original.use(0)
        self.texture_vertical_blur.use(1)
        self.combine_vao.render()

        # Read the pixels back from the intermediate combined texture
        pixels = intermediate_combined_texture.read()

        # Create a new Pygame surface from the pixels
        bloomed_surface = pygame.image.frombytes(pixels, (width, height), "RGBA").convert_alpha()

        # Release textures and framebuffers
        texture_original.release()
        intermediate_combined_texture.release()
        fbo_intermediate_combined.release()

        # Restore the default framebuffer (screen)
        self.ctx.fbo = None

        return bloomed_surface

    def release(self):
        """Releases OpenGL resources."""
        self.horizontal_blur_program.release()
        self.vertical_blur_program.release()
        self.combine_program.release()
        self.vbo.release()
        self.ibo.release()
        self.texture_horizontal_blur.release()
        self.texture_vertical_blur.release()
        self.fbo_horizontal_blur.release()
        self.fbo_vertical_blur.release()

