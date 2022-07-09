"""empty message

Revision ID: 768887c3d309
Revises: 
Create Date: 2022-07-08 03:15:35.760604

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import sqlmodel
import jheep


# revision identifiers, used by Alembic.
revision = '768887c3d309'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('modelstore',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('created_at', jheep.models.types.TIMESTAMPAware(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', jheep.models.types.TIMESTAMPAware(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('url')
    )
    op.create_index(op.f('ix_modelstore_created_at'), 'modelstore', ['created_at'], unique=False)
    op.create_index(op.f('ix_modelstore_updated_at'), 'modelstore', ['updated_at'], unique=False)
    op.create_table('song',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('created_at', jheep.models.types.TIMESTAMPAware(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', jheep.models.types.TIMESTAMPAware(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('artist', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name', 'artist')
    )
    op.create_index(op.f('ix_song_created_at'), 'song', ['created_at'], unique=False)
    op.create_index(op.f('ix_song_updated_at'), 'song', ['updated_at'], unique=False)
    op.create_table('model',
    sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
    sa.Column('created_at', jheep.models.types.TIMESTAMPAware(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', jheep.models.types.TIMESTAMPAware(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('path', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('modelstore_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.ForeignKeyConstraint(['modelstore_id'], ['modelstore.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('modelstore_id', 'path')
    )
    op.create_index(op.f('ix_model_created_at'), 'model', ['created_at'], unique=False)
    op.create_index(op.f('ix_model_updated_at'), 'model', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_model_updated_at'), table_name='model')
    op.drop_index(op.f('ix_model_created_at'), table_name='model')
    op.drop_table('model')
    op.drop_index(op.f('ix_song_updated_at'), table_name='song')
    op.drop_index(op.f('ix_song_created_at'), table_name='song')
    op.drop_table('song')
    op.drop_index(op.f('ix_modelstore_updated_at'), table_name='modelstore')
    op.drop_index(op.f('ix_modelstore_created_at'), table_name='modelstore')
    op.drop_table('modelstore')
    # ### end Alembic commands ###